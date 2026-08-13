# -*- coding: utf-8 -*-
"""
Atana Tools — Project Sync (PyRevit)
====================================
Schema: atana-revit-sync/2.0

Reads the project DB JSON exported from the Atana IM app and:
  1. Sets Project Information (built-in + ATA_ZZ_* shared parameters)
  2. Sets / creates Global Parameters (GLOBAL_ZZ_*)
  3. Derives task team from the model file name (ISO role segment)
  4. Bulk-updates title block Designed By (TTM) / Checked By (Peer)
  5. Builds a Publish Set named for the current work stage and adds matched DR/SH sheets
  6. Writes a sheet-inventory JSON (merge by documentId) for the app to re-import

INSTALL (once)
--------------
1. Install pyRevit: https://pyrevitlabs.notion.site
2. Create folder:
     %APPDATA%\\pyRevit\\Extensions\\AtanaTools.extension\\AtanaTools.tab\\ProjectSync.panel\\ProjectSync.pushbutton\
3. Copy this file as `script.py` into that pushbutton folder.
4. Copy `ATA_ZZ_SharedParameters.txt` next to `script.py` (or set SHARED_PARAM_FILE below).
5. Reload pyRevit (pyRevit → Reload).
6. In Revit: AtanaTools tab → Project Sync.

APP SIDE
--------
1. In Atana IM → Edit project → fill project info + organogram + import MIDP plan.
2. Export / push the DB JSON to ACC (or download locally).
3. First run of this button asks for the folder that contains that JSON.
   Path is remembered per Windows user in %APPDATA%\\AtanaTools\\sync_path.txt

NAMING
------
Model file should follow ISO naming so role can be parsed, e.g.:
  MD6357-ATA-XX-XX-M3-AR-0001.rvt  → role = AR
"""

from __future__ import print_function

import os
import re
import json
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("System")

from Autodesk.Revit.DB import (
    FilteredElementCollector, BuiltInCategory, BuiltInParameter,
    Transaction, ElementId, StorageType, GlobalParameter,
    DoubleParameterValue, IntegerParameterValue, StringParameterValue,
    SpecTypeId, ParameterType, DefinitionFile, ExternalDefinitionCreationOptions,
    SharedParameterElement, CategorySet, InstanceBinding, TypeBinding,
    ViewSheet, PrintManager, ViewSet, ViewSheetSetting
)
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
from System.Windows.Forms import OpenFileDialog, DialogResult, FolderBrowserDialog
from System.IO import File, Directory, Path

try:
    from Autodesk.Revit.DB import LabelUtils
except Exception:
    LabelUtils = None

# pyRevit doc/uidoc
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

SYNC_SCHEMA = "atana-revit-sync/2.0"

SHARED_GUIDS = {
    "ATA_ZZ_ClientContractNumber": "28b55e4c-650c-4af5-aae2-5ae0a0cda589",
    "ATA_ZZ_ProjectDiscipline":     "60119a77-63b3-451e-969d-768d3b01fce0",
    "ATA_ZZ_ProjectStage":          "b00f059e-1c43-446a-ad66-b7826e488c8f",
}

# Built-in Project Information keys we write
PI_BUILTIN = {
    "Project Number":   BuiltInParameter.PROJECT_NUMBER,
    "Project Name":     BuiltInParameter.PROJECT_NAME,
    "Client Name":      BuiltInParameter.CLIENT_NAME,
    "Project Address":  BuiltInParameter.PROJECT_ADDRESS,
    "Organization Name": BuiltInParameter.PROJECT_ORGANIZATION_NAME,
}

GLOBAL_NAMES = [
    "GLOBAL_ZZ_ClientContractNumber",
    "GLOBAL_ZZ_ProjectDiscipline",
    "GLOBAL_ZZ_ProjectStage",          # integer
    "GLOBAL_ZZ_ProjectDeliveryManager",
    "GLOBAL_ZZ_InformationManager",
]

TITLEBLOCK_DESIGNED = ["Designed By", "Designed by", "DESIGNED BY", "Drawn By", "Author"]
TITLEBLOCK_CHECKED  = ["Checked By", "Checked by", "CHECKED BY", "Approved By", "Approved by"]

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AtanaTools")
CONFIG_PATH = os.path.join(CONFIG_DIR, "sync_path.txt")

# Optional: absolute path to shared-parameter definition file shipped with the button
SHARED_PARAM_FILE = os.path.join(os.path.dirname(__file__), "ATA_ZZ_SharedParameters.txt")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def info(msg, title="Atana Project Sync"):
    TaskDialog.Show(title, str(msg))

def confirm(msg, title="Atana Project Sync"):
    r = TaskDialog.Show(title, str(msg), TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No)
    return r == TaskDialogResult.Yes

def load_sync_folder():
    if File.Exists(CONFIG_PATH):
        try:
            p = File.ReadAllText(CONFIG_PATH).strip()
            if p and Directory.Exists(p):
                return p
        except Exception:
            pass
    return None

def save_sync_folder(path):
    if not Directory.Exists(CONFIG_DIR):
        Directory.CreateDirectory(CONFIG_DIR)
    File.WriteAllText(CONFIG_PATH, path)

def pick_folder(prompt="Select folder that contains the Atana DB JSON"):
    dlg = FolderBrowserDialog()
    dlg.Description = prompt
    if dlg.ShowDialog() == DialogResult.OK:
        return dlg.SelectedPath
    return None

def pick_json_file(start_dir=None):
    dlg = OpenFileDialog()
    dlg.Filter = "Atana DB JSON (*.json)|*.json|All files (*.*)|*.*"
    dlg.Title = "Select Atana project DB JSON"
    if start_dir and Directory.Exists(start_dir):
        dlg.InitialDirectory = start_dir
    if dlg.ShowDialog() == DialogResult.OK:
        return dlg.FileName
    return None

def find_db_json(folder):
    """Prefer *DB*IM*.json or *DB*.json in folder (non-recursive first, then 1 level)."""
    if not folder or not Directory.Exists(folder):
        return None
    candidates = []
    for root, dirs, files in os.walk(folder):
        depth = root[len(folder):].count(os.sep)
        if depth > 1:
            dirs[:] = []
            continue
        for f in files:
            if not f.lower().endswith(".json"):
                continue
            low = f.lower()
            if "db" in low and ("im" in low or "sync" in low or "atana" in low):
                candidates.append((0, os.path.join(root, f)))
            elif "db" in low:
                candidates.append((1, os.path.join(root, f)))
            elif "atana" in low or "revit-sync" in low:
                candidates.append((2, os.path.join(root, f)))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1] if candidates else None

def load_pack(path):
    with open(path, "r") as fh:
        data = json.load(fh)
    return data

def parse_role_from_model_name(path_or_name):
    """ISO: Project-Originator-Func-Spatial-Form-Role-Number → role is 2nd last token."""
    base = os.path.splitext(os.path.basename(path_or_name or ""))[0]
    parts = base.split("-")
    if len(parts) >= 6:
        return parts[-2].upper()
    # fallback: look for known role codes
    known = ("AR", "ST", "CV", "EE", "ME", "MH", "PD", "PS", "FP", "IM", "ZZ")
    for p in parts:
        if p.upper() in known:
            return p.upper()
    return ""

def model_path():
    try:
        if doc.PathName:
            return doc.PathName
    except Exception:
        pass
    return doc.Title or "Untitled"


# ---------------------------------------------------------------------------
# Shared parameters
# ---------------------------------------------------------------------------

def ensure_shared_params():
    """Bind ATA_ZZ_* shared parameters to Project Information if missing."""
    if not File.Exists(SHARED_PARAM_FILE):
        # still OK if parameters already exist in the model
        return False

    # Open definition file
    prev = app.SharedParametersFilename
    try:
        app.SharedParametersFilename = SHARED_PARAM_FILE
        def_file = app.OpenSharedParameterFile()
        if def_file is None:
            return False
        group = None
        for g in def_file.Groups:
            group = g
            break
        if group is None:
            return False

        pi_cat = doc.Settings.Categories.get_Item(BuiltInCategory.OST_ProjectInformation)
        cats = app.Create.NewCategorySet()
        cats.Insert(pi_cat)
        binding_map = doc.ParameterBindings

        t = Transaction(doc, "Atana — ensure shared parameters")
        t.Start()
        try:
            for name, guid in SHARED_GUIDS.items():
                # already present?
                found = False
                it = binding_map.ForwardIterator()
                it.Reset()
                while it.MoveNext():
                    defn = it.Key
                    if defn and defn.Name == name:
                        found = True
                        break
                if found:
                    continue
                # create from definition file
                ext_def = None
                for d in group.Definitions:
                    if d.Name == name:
                        ext_def = d
                        break
                if ext_def is None:
                    continue
                binding = app.Create.NewInstanceBinding(cats)
                binding_map.Insert(ext_def, binding, BuiltInParameterGroup.PG_DATA)
        finally:
            t.Commit()
        return True
    except Exception as ex:
        print("ensure_shared_params:", ex)
        return False
    finally:
        try:
            app.SharedParametersFilename = prev
        except Exception:
            pass


def get_project_info_element():
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectInformation)
    for e in col:
        return e
    return None


def set_pi_builtin(pi, bip, value):
    if value is None:
        return False
    p = pi.get_Parameter(bip)
    if p is None or p.IsReadOnly:
        return False
    try:
        if p.StorageType == StorageType.String:
            cur = p.AsString() or ""
            if cur == str(value):
                return False
            p.Set(str(value))
            return True
    except Exception as ex:
        print("set_pi_builtin", bip, ex)
    return False


def set_pi_shared_by_name(pi, name, value):
    if value is None:
        return False
    for p in pi.Parameters:
        if p.Definition and p.Definition.Name == name:
            if p.IsReadOnly:
                return False
            try:
                if p.StorageType == StorageType.String:
                    cur = p.AsString() or ""
                    if cur == str(value):
                        return False
                    p.Set(str(value))
                    return True
            except Exception as ex:
                print("set_pi_shared", name, ex)
            return False
    return False


def read_pi_value(pi, name_or_bip):
    if isinstance(name_or_bip, BuiltInParameter):
        p = pi.get_Parameter(name_or_bip)
        return (p.AsString() if p else "") or ""
    for p in pi.Parameters:
        if p.Definition and p.Definition.Name == name_or_bip:
            return (p.AsString() if p else "") or ""
    return ""


# ---------------------------------------------------------------------------
# Global parameters
# ---------------------------------------------------------------------------

def find_global(name):
    for gp in FilteredElementCollector(doc).OfClass(GlobalParameter):
        if gp.Name == name:
            return gp
    return None


def ensure_global(name, is_integer=False):
    gp = find_global(name)
    if gp:
        return gp
    t = Transaction(doc, "Atana — create global " + name)
    t.Start()
    try:
        # Text vs Integer
        try:
            # Newer Revit: SpecTypeId
            if is_integer:
                gp = GlobalParameter.Create(doc, name, SpecTypeId.Int.Integer)
            else:
                gp = GlobalParameter.Create(doc, name, SpecTypeId.String.Text)
        except Exception:
            # Older API fallback
            from Autodesk.Revit.DB import ParameterType as PT
            if is_integer:
                gp = GlobalParameter.Create(doc, name, PT.Integer)
            else:
                gp = GlobalParameter.Create(doc, name, PT.Text)
        t.Commit()
        return gp
    except Exception as ex:
        t.RollBack()
        print("ensure_global", name, ex)
        return None


def set_global(name, value, is_integer=False):
    gp = ensure_global(name, is_integer=is_integer)
    if gp is None:
        return False
    t = Transaction(doc, "Atana — set global " + name)
    t.Start()
    try:
        if is_integer:
            iv = int(value) if value not in (None, "") else 0
            gp.SetValue(IntegerParameterValue(iv))
        else:
            gp.SetValue(StringParameterValue(str(value or "")))
        t.Commit()
        return True
    except Exception as ex:
        t.RollBack()
        print("set_global", name, ex)
        return False


def read_global(name, is_integer=False):
    gp = find_global(name)
    if not gp:
        return None
    try:
        val = gp.GetValue()
        if is_integer:
            return int(val.Value) if val else None
        return str(val.Value) if val else ""
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Title blocks
# ---------------------------------------------------------------------------

def iter_titleblock_instances():
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType()
    for e in col:
        yield e


def param_by_names(el, names):
    for n in names:
        for p in el.Parameters:
            if p.Definition and p.Definition.Name == n:
                return p
    # type params
    try:
        t = doc.GetElement(el.GetTypeId())
        if t:
            for n in names:
                for p in t.Parameters:
                    if p.Definition and p.Definition.Name == n:
                        return p
    except Exception:
        pass
    return None


def apply_titleblocks(designed_by, checked_by):
    changed = 0
    t = Transaction(doc, "Atana — title block names")
    t.Start()
    try:
        for tb in iter_titleblock_instances():
            if designed_by:
                p = param_by_names(tb, TITLEBLOCK_DESIGNED)
                if p and not p.IsReadOnly and p.StorageType == StorageType.String:
                    if (p.AsString() or "") != designed_by:
                        p.Set(designed_by)
                        changed += 1
            if checked_by:
                p = param_by_names(tb, TITLEBLOCK_CHECKED)
                if p and not p.IsReadOnly and p.StorageType == StorageType.String:
                    if (p.AsString() or "") != checked_by:
                        p.Set(checked_by)
                        changed += 1
        t.Commit()
    except Exception as ex:
        t.RollBack()
        print("apply_titleblocks", ex)
    return changed


# ---------------------------------------------------------------------------
# Publish set (ViewSheetSetting)
# ---------------------------------------------------------------------------

def sheets_in_model():
    out = []
    for vs in FilteredElementCollector(doc).OfClass(ViewSheet):
        try:
            out.append(vs)
        except Exception:
            pass
    return out


def normalize_id(s):
    return re.sub(r"\s+", "", str(s or "").upper())


def match_sheets_to_plan(plan_rows, role_code):
    """Return ViewSheet list whose number or name matches plan DR/SH for this role."""
    if not plan_rows:
        return []
    wanted = set()
    for r in plan_rows:
        form = str(r.get("form") or "").upper()
        row_role = str(r.get("role") or "").upper()
        if role_code and row_role and row_role != role_code:
            continue
        if form and form not in ("DR", "SH", "M3", "M2", "M1"):
            # still allow if sheet number looks like a drawing
            pass
        doc_id = r.get("documentId") or r.get("isoNumber") or ""
        sheet_no = r.get("sheetNumber") or ""
        if doc_id:
            wanted.add(normalize_id(doc_id))
            # last token often is the number
            parts = str(doc_id).split("-")
            if parts:
                wanted.add(normalize_id(parts[-1]))
        if sheet_no:
            wanted.add(normalize_id(sheet_no))

    matched = []
    for vs in sheets_in_model():
        num = normalize_id(vs.SheetNumber)
        name = normalize_id(vs.Name)
        if num in wanted or name in wanted:
            matched.append(vs)
            continue
        # fuzzy: sheet number appears as last segment of an iso id
        for w in wanted:
            if w.endswith(num) or num and num in w:
                matched.append(vs)
                break
    return matched


def create_or_update_publish_set(set_name, sheets):
    """Create/replace a print set (publish set) with the given sheets."""
    if not sheets:
        return 0
    pm = doc.PrintManager
    try:
        pm.PrintRange = pm.PrintRange.Select
    except Exception:
        pass
    vss = pm.ViewSheetSetting
    t = Transaction(doc, "Atana — publish set " + set_name)
    t.Start()
    try:
        # Delete existing set with same name if present
        try:
            existing = vss.GetViewSheets()  # may not list named sets on all versions
        except Exception:
            existing = None
        # Build ViewSet
        vs = ViewSet()
        for s in sheets:
            vs.Insert(s)
        # Save as named set
        try:
            # In-session current set
            vss.CurrentViewSheetSet.Views = vs
            try:
                vss.SaveAs(set_name)
            except Exception:
                # already exists — delete and re-save
                try:
                    vss.Delete()
                except Exception:
                    pass
                try:
                    vss.SaveAs(set_name)
                except Exception as ex2:
                    print("SaveAs failed", ex2)
        except Exception as ex:
            print("publish set", ex)
        t.Commit()
        return len(list(sheets))
    except Exception as ex:
        t.RollBack()
        print("create_or_update_publish_set", ex)
        return 0


# ---------------------------------------------------------------------------
# Sheet inventory export (merge)
# ---------------------------------------------------------------------------

def export_sheet_inventory(folder, role_code, pack):
    """Write/merge sheet inventory JSON for this task team."""
    if not folder:
        return None
    model = os.path.basename(model_path())
    inv_name = "SHEETS-{}-INVENTORY.json".format(role_code or "ZZ")
    inv_path = os.path.join(folder, inv_name)

    existing = []
    if File.Exists(inv_path):
        try:
            with open(inv_path, "r") as fh:
                data = json.load(fh)
            existing = data.get("sheets") or data.get("rows") or []
        except Exception:
            existing = []

    by_id = {}
    for r in existing:
        key = normalize_id(r.get("documentId") or r.get("sheetNumber") or r.get("id"))
        if key:
            by_id[key] = r

    for vs in sheets_in_model():
        rec = {
            "documentId": vs.SheetNumber,
            "sheetNumber": vs.SheetNumber,
            "sheetName": vs.Name,
            "role": role_code,
            "form": "SH",
            "revision": "",
            "modelName": model,
            "updatedAt": None,
            "updatedBy": os.environ.get("USERNAME", ""),
        }
        key = normalize_id(vs.SheetNumber)
        by_id[key] = rec

    out = {
        "schema": "atana-sheet-inventory/1.0",
        "role": role_code,
        "modelName": model,
        "sheets": list(by_id.values()),
    }
    with open(inv_path, "w") as fh:
        json.dump(out, fh, indent=2)
    return inv_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # 1) Locate DB JSON
    folder = load_sync_folder()
    if not folder:
        folder = pick_folder("Select the ACC/local folder that holds the Atana DB JSON")
        if not folder:
            info("Cancelled — no folder selected.")
            return
        save_sync_folder(folder)

    json_path = find_db_json(folder)
    if not json_path:
        json_path = pick_json_file(folder)
        if not json_path:
            info("No DB JSON found in:\n{}\n\nExport it from Atana IM (Revit / DB sync) first.".format(folder))
            return
        # remember parent
        save_sync_folder(os.path.dirname(json_path))
        folder = os.path.dirname(json_path)

    try:
        pack = load_pack(json_path)
    except Exception as ex:
        info("Could not read JSON:\n{}\n\n{}".format(json_path, ex))
        return

    pi_src = pack.get("projectInformation") or {}
    gp_src = pack.get("globalParameters") or {}
    tb_map = (pack.get("titleBlocks") or {}).get("byTaskTeam") or {}
    plan_rows = pack.get("deliverables") or pack.get("planRows") or []
    stage = (pack.get("workStage") or {})
    stage_code = stage.get("code") or pi_src.get("ATA_ZZ_ProjectStage") or "WS1"

    # 2) Role from model name
    role = parse_role_from_model_name(model_path())
    if not role:
        role = pi_src.get("ATA_ZZ_ProjectDiscipline") or ""
    if not role:
        info("Could not determine task team from model file name.\n"
             "Name the model with an ISO role segment (e.g. …-AR-0001.rvt).")
        # continue anyway

    team_info = tb_map.get(role) or {}
    designed_by = team_info.get("designedBy") or ""
    checked_by = team_info.get("approvedBy") or team_info.get("checkedBy") or ""

    # 3) Ensure shared params exist
    ensure_shared_params()

    pi = get_project_info_element()
    if pi is None:
        info("No Project Information element found.")
        return

    # 4) Diff project information
    desired_pi = {
        "Project Number":   pi_src.get("Project Number") or pi_src.get("projectNumber") or "",
        "Project Name":     pi_src.get("Project Name") or pi_src.get("projectName") or "",
        "Client Name":      pi_src.get("Client Name") or pi_src.get("clientName") or "",
        "Project Address":  pi_src.get("Project Address") or pi_src.get("projectAddress") or "",
        "Organization Name": pi_src.get("Organization Name") or pi_src.get("organizationName") or "",
        "ATA_ZZ_ClientContractNumber": pi_src.get("ATA_ZZ_ClientContractNumber") or "",
        "ATA_ZZ_ProjectDiscipline": role or pi_src.get("ATA_ZZ_ProjectDiscipline") or "",
        "ATA_ZZ_ProjectStage": pi_src.get("ATA_ZZ_ProjectStage") or stage_code,
    }

    mismatches = []
    for k, new_v in desired_pi.items():
        if not new_v:
            continue
        bip = PI_BUILTIN.get(k)
        cur = read_pi_value(pi, bip if bip is not None else k)
        if (cur or "") != str(new_v):
            mismatches.append((k, cur, new_v))

    if mismatches:
        lines = ["Project Information differs from Atana pack:\n"]
        for k, cur, new_v in mismatches:
            lines.append("• {}: \"{}\" → \"{}\"".format(k, cur, new_v))
        lines.append("\nUpdate all listed values?")
        if confirm("\n".join(lines)):
            t = Transaction(doc, "Atana — project information")
            t.Start()
            try:
                for k, cur, new_v in mismatches:
                    bip = PI_BUILTIN.get(k)
                    if bip is not None:
                        set_pi_builtin(pi, bip, new_v)
                    else:
                        set_pi_shared_by_name(pi, k, new_v)
                t.Commit()
            except Exception as ex:
                t.RollBack()
                info("Failed to write Project Information:\n{}".format(ex))
                return
    else:
        print("Project Information already matches pack.")

    # 5) Global parameters
    gp_desired = {
        "GLOBAL_ZZ_ClientContractNumber": gp_src.get("GLOBAL_ZZ_ClientContractNumber") or desired_pi["ATA_ZZ_ClientContractNumber"],
        "GLOBAL_ZZ_ProjectDiscipline": role or gp_src.get("GLOBAL_ZZ_ProjectDiscipline") or "",
        "GLOBAL_ZZ_ProjectStage": gp_src.get("GLOBAL_ZZ_ProjectStage") or int(re.sub(r"\D", "") or 0) or 1,
        "GLOBAL_ZZ_ProjectDeliveryManager": gp_src.get("GLOBAL_ZZ_ProjectDeliveryManager") or "",
        "GLOBAL_ZZ_InformationManager": gp_src.get("GLOBAL_ZZ_InformationManager") or "",
    }
    # stage integer
    try:
        stage_int = int(gp_desired["GLOBAL_ZZ_ProjectStage"])
    except Exception:
        m = re.search(r"(\d+)", str(stage_code))
        stage_int = int(m.group(1)) if m else 1
    gp_desired["GLOBAL_ZZ_ProjectStage"] = stage_int

    gp_mismatch = []
    for name, val in gp_desired.items():
        is_int = name.endswith("ProjectStage")
        cur = read_global(name, is_integer=is_int)
        if cur is None or str(cur) != str(val):
            gp_mismatch.append((name, cur, val, is_int))

    if gp_mismatch:
        lines = ["Global Parameters differ:\n"]
        for n, cur, val, _ in gp_mismatch:
            lines.append("• {}: {} → {}".format(n, cur, val))
        lines.append("\nUpdate globals?")
        if confirm("\n".join(lines)):
            for n, cur, val, is_int in gp_mismatch:
                set_global(n, val, is_integer=is_int)

    # 6) Title blocks (bulk one confirmation)
    if designed_by or checked_by:
        msg = ("Title blocks for task team {}:\n\n"
               "Designed By (TTM): {}\n"
               "Checked By (Peer): {}\n\n"
               "Apply to all title blocks in this model?").format(
                   role or "—", designed_by or "—", checked_by or "—")
        if confirm(msg):
            n = apply_titleblocks(designed_by, checked_by)
            info("Updated parameters on {} title block instance(s).".format(n))

    # 7) Publish set
    matched = match_sheets_to_plan(plan_rows, role)
    set_name = stage_code if stage_code else "WS1"
    # normalise S3 → keep as provided; also accept SW3 style
    if set_name.startswith("S") and not set_name.startswith("WS"):
        set_name = "WS" + set_name[1:]
    if matched:
        msg = ("Publish Set \"{}\"\n\n"
               "Matched {} sheet(s) from the MIDP plan for role {}.\n"
               "Create / replace this publish set?").format(set_name, len(matched), role or "all")
        if confirm(msg):
            n = create_or_update_publish_set(set_name, matched)
            info("Publish set \"{}\" now has {} sheet(s).\n"
                 "Use this set when exporting to Revizto / ACC.".format(set_name, n))
    else:
        print("No plan sheets matched for role", role)

    # 8) Sheet inventory merge export
    inv = export_sheet_inventory(folder, role or "ZZ", pack)
    if inv:
        print("Sheet inventory written:", inv)

    info(
        "Project Sync complete.\n\n"
        "JSON: {}\n"
        "Role: {}\n"
        "Stage: {}\n"
        "Publish set: {}\n"
        "Sheet inventory: {}".format(
            os.path.basename(json_path),
            role or "—",
            stage_code,
            set_name,
            os.path.basename(inv) if inv else "—"
        )
    )


if __name__ == "__main__":
    main()
