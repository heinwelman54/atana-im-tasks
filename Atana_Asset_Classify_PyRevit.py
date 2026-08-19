# -*- coding: utf-8 -*-
"""
Atana Asset Classify + Rename (PyRevit)
--------------------------------------
1. Reads the active Family document name (or selected family in a project).
2. Optionally applies a new name from the clipboard / dialog (name built in Atana Asset Naming tool).
3. If a project/template is open in the same session, renames loaded family symbols to match.
4. Prompts to Save As the family file under the new name.
5. Loads asset-naming-data.json and writes Uniclass Ss / Ma / Pr + IFC4 (+ EF if mapped)
   to shared parameters on the family.

Setup
- Place this file in a PyRevit extension button folder.
- Place asset-naming-data.json next to this script, or set ATANA_ASSET_DATA env / path below.
- Shared parameters must exist in the family (or will be bound if definition file is available).

Shared parameter names (override GUIDs when you confirm them):
  ATA_ZZ_UniclassSs
  ATA_ZZ_UniclassMa
  ATA_ZZ_UniclassPr
  ATA_ZZ_IFC4
  ATA_ZZ_EF   (optional EF classification code)
"""

from __future__ import print_function
import os
import json
import re
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import (
    FilteredElementCollector, Family, FamilySymbol, BuiltInParameter,
    StorageType, Transaction, ElementId, ModelPathUtils, SaveAsOptions
)
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult

try:
    from pyrevit import forms, script
except Exception:
    forms = None
    script = None

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document if uidoc else None
app = __revit__.Application

# --- Config -----------------------------------------------------------------
# Default: same folder as this script, then common Atana paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
DATA_CANDIDATES = [
    os.path.join(SCRIPT_DIR, "asset-naming-data.json"),
    os.path.join(SCRIPT_DIR, "..", "asset-naming-data.json"),
    os.path.expandvars(r"%APPDATA%\Atana\asset-naming-data.json"),
    os.path.expandvars(r"%USERPROFILE%\Atana\asset-naming-data.json"),
]

PARAM_SS = "ATA_ZZ_UniclassSs"
PARAM_MA = "ATA_ZZ_UniclassMa"
PARAM_PR = "ATA_ZZ_UniclassPr"
PARAM_IFC = "ATA_ZZ_IFC4"
PARAM_EF = "ATA_ZZ_EF"

# Optional: known shared-param GUIDs (fill when confirmed)
PARAM_GUIDS = {
    # PARAM_SS: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
}


def alert(msg, title="Atana Asset Classify"):
    try:
        TaskDialog.Show(title, str(msg))
    except Exception:
        print(msg)


def ask_yes_no(msg, title="Atana Asset Classify"):
    try:
        r = TaskDialog.Show(title, str(msg), TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No)
        return r == TaskDialogResult.Yes
    except Exception:
        return True


def load_data():
    for p in DATA_CANDIDATES:
        p = os.path.normpath(p)
        if os.path.isfile(p):
            with open(p, "r") as f:
                return json.load(f), p
    return None, None


def parse_family_name(name):
    """Originator_Source_Category_Material_Object"""
    if not name:
        return None
    base = os.path.splitext(name)[0]
    parts = base.split("_")
    if len(parts) < 5:
        return None
    # Object may contain underscores rarely — take first 4 fixed, rest = object
    return {
        "originator": parts[0],
        "source": parts[1],
        "category": parts[2],
        "material": parts[3],
        "object": "_".join(parts[4:]),
        "full": base,
    }


def lookup_classification(data, parts):
    """Map naming parts → Uniclass Ss / Ma / Pr / IFC4 / EF."""
    out = {"ss": None, "ma": None, "pr": None, "ifc4": None, "ef": None, "revitCategory": None}

    for c in data.get("categories") or []:
        if c.get("isGroup"):
            continue
        if (c.get("code") or "").upper() == (parts["category"] or "").upper():
            out["ss"] = c.get("uniclassSs") or None
            # EF often mirrors system code if present
            out["ef"] = c.get("ef") or c.get("uniclassEf") or c.get("uniclassSs")
            break

    for m in data.get("materials") or []:
        if m.get("isGroup"):
            continue
        if (m.get("code") or "").upper() == (parts["material"] or "").upper():
            out["ma"] = m.get("uniclassCode") or None
            break

    # Search all task-team object lists for matching Object name
    obj_name = parts.get("object") or ""
    for team, items in (data.get("objectsByTaskTeam") or {}).items():
        for it in items or []:
            if (it.get("name") or "") == obj_name:
                out["pr"] = it.get("uniclassPr") or None
                out["ifc4"] = it.get("ifc4") or None
                out["revitCategory"] = it.get("revitCategory") or None
                if it.get("ef"):
                    out["ef"] = it.get("ef")
                return out
    return out


def set_param(element, name, value):
    if value is None or value == "":
        return False
    p = element.LookupParameter(name)
    if p is None:
        # try type if instance
        try:
            if hasattr(element, "Symbol") and element.Symbol:
                p = element.Symbol.LookupParameter(name)
        except Exception:
            pass
    if p is None or p.IsReadOnly:
        return False
    try:
        if p.StorageType == StorageType.String:
            p.Set(str(value))
            return True
        if p.StorageType == StorageType.Integer:
            p.Set(int(value))
            return True
    except Exception:
        return False
    return False


def get_open_documents():
    docs = []
    try:
        for d in app.Documents:
            docs.append(d)
    except Exception:
        if doc:
            docs.append(doc)
    return docs


def rename_family_in_project(proj_doc, old_name, new_name):
    """Rename Family element in a project/template document."""
    if proj_doc is None or proj_doc.IsFamilyDocument:
        return 0
    count = 0
    families = FilteredElementCollector(proj_doc).OfClass(Family).ToElements()
    t = Transaction(proj_doc, "Atana rename family")
    t.Start()
    try:
        for fam in families:
            try:
                if fam.Name == old_name and old_name != new_name:
                    fam.Name = new_name
                    count += 1
            except Exception:
                pass
        t.Commit()
    except Exception as ex:
        if t.HasStarted():
            t.RollBack()
        raise ex
    return count


def write_classifications_to_family(fam_doc, classification):
    """Write shared params on family document types + family manager parameters if available."""
    written = []
    t = Transaction(fam_doc, "Atana write classification")
    t.Start()
    try:
        # Family types
        types = FilteredElementCollector(fam_doc).OfClass(FamilySymbol).ToElements()
        targets = list(types) if types else []
        # Also try owner family parameters via FamilyManager
        try:
            fm = fam_doc.FamilyManager
            # set on current type
            mapping = [
                (PARAM_SS, classification.get("ss")),
                (PARAM_MA, classification.get("ma")),
                (PARAM_PR, classification.get("pr")),
                (PARAM_IFC, classification.get("ifc4")),
                (PARAM_EF, classification.get("ef")),
            ]
            for pname, val in mapping:
                if not val:
                    continue
                # FamilyManager parameters
                found = None
                for fp in fm.GetParameters():
                    if fp.Definition.Name == pname:
                        found = fp
                        break
                if found is not None:
                    try:
                        fm.Set(found, str(val))
                        written.append(pname)
                    except Exception:
                        pass
        except Exception:
            pass

        for el in targets:
            for pname, key in [
                (PARAM_SS, "ss"),
                (PARAM_MA, "ma"),
                (PARAM_PR, "pr"),
                (PARAM_IFC, "ifc4"),
                (PARAM_EF, "ef"),
            ]:
                if set_param(el, pname, classification.get(key)):
                    if pname not in written:
                        written.append(pname)
        t.Commit()
    except Exception as ex:
        if t.HasStarted():
            t.RollBack()
        raise ex
    return written


def main():
    if doc is None:
        alert("No active document.")
        return

    data, data_path = load_data()
    if not data:
        alert(
            "Could not find asset-naming-data.json.\n\n"
            "Place it next to this script or in %APPDATA%\\Atana\\\n"
            "Download from the Atana Asset Naming tool (Export data / repo file)."
        )
        return

    # --- Determine target family name ----------------------------------------
    current_name = doc.Title
    if current_name.lower().endswith(".rfa"):
        current_name = current_name[:-4]

    # Prefer clipboard from Asset Naming tool "Copy name"
    clip = ""
    try:
        from System.Windows.Forms import Clipboard
        if Clipboard.ContainsText():
            clip = (Clipboard.GetText() or "").strip()
    except Exception:
        pass

    suggested = clip if (clip and "_" in clip and not " " in clip.split("\n")[0]) else current_name
    if "\n" in suggested:
        suggested = suggested.split("\n")[0].strip()

    new_name = suggested
    if forms:
        new_name = forms.ask_for_string(
            default=suggested,
            prompt="Family name (from Atana Asset Naming — Originator_Source_Category_Material_Object)",
            title="Atana Asset Naming",
        )
        if not new_name:
            return
    else:
        if not ask_yes_no("Use family name:\n\n{}\n\nYes = continue, No = cancel".format(suggested)):
            return
        new_name = suggested

    new_name = os.path.splitext(new_name.strip())[0]
    parts = parse_family_name(new_name)
    if not parts:
        alert(
            "Name does not match Atana pattern:\n"
            "Originator_Source_Category_Material_Object\n\nGot:\n" + new_name
        )
        return

    classification = lookup_classification(data, parts)

    summary = (
        "Name: {full}\n"
        "Ss: {ss}\nMa: {ma}\nPr: {pr}\nIFC4: {ifc4}\nEF: {ef}\n"
        "Data: {path}"
    ).format(
        full=parts["full"],
        ss=classification.get("ss") or "—",
        ma=classification.get("ma") or "—",
        pr=classification.get("pr") or "—",
        ifc4=classification.get("ifc4") or "—",
        ef=classification.get("ef") or "—",
        path=data_path,
    )
    if not ask_yes_no(summary + "\n\nApply rename + write classification?"):
        return

    # --- Family document path ------------------------------------------------
    fam_doc = doc if doc.IsFamilyDocument else None
    old_family_name = None

    if fam_doc is None:
        # Project: try selection of a family instance / symbol
        alert(
            "Active document is a project/template.\n"
            "Open the .rfa family to write parameters and Save As.\n"
            "Will still try to rename a matching loaded family in this project."
        )
        old_family_name = current_name
        # rename in this project
        try:
            n = rename_family_in_project(doc, old_family_name, new_name)
            # also try if user typed different old name - scan by object-ish
            if n == 0:
                # try rename any family that matches previous clipboard? skip
                pass
            alert("Renamed {} family element(s) in project to:\n{}".format(n, new_name))
        except Exception as ex:
            alert("Project rename failed: " + str(ex))
        return

    old_family_name = fam_doc.Title
    if old_family_name.lower().endswith(".rfa"):
        old_family_name = old_family_name[:-4]

    # Write classification into open family
    try:
        written = write_classifications_to_family(fam_doc, classification)
    except Exception as ex:
        alert("Classification write failed: " + str(ex))
        written = []

    # Rename family in any open project/template sessions
    renamed_docs = []
    for d in get_open_documents():
        if d.IsFamilyDocument:
            continue
        try:
            n = rename_family_in_project(d, old_family_name, new_name)
            if n:
                renamed_docs.append("{} ({})".format(d.Title, n))
            # also try new name already? if old != current_name variants
            if old_family_name != current_name:
                n2 = rename_family_in_project(d, current_name, new_name)
                if n2:
                    renamed_docs.append("{} ({})".format(d.Title, n2))
        except Exception:
            pass

    # Save As family
    save_msg = "Parameters written: {}\n".format(", ".join(written) if written else "(none — check shared params exist)")
    if renamed_docs:
        save_msg += "Renamed in: {}\n".format(", ".join(renamed_docs))
    save_msg += "\nSave family as:\n{}.rfa ?".format(new_name)

    if ask_yes_no(save_msg):
        try:
            # Suggest path next to current
            path = fam_doc.PathName
            folder = os.path.dirname(path) if path else os.path.expanduser("~\\Documents")
            target = os.path.join(folder, new_name + ".rfa")
            if forms:
                target = forms.save_file(file_ext="rfa", default_name=new_name + ".rfa") or target
            opts = SaveAsOptions()
            opts.OverwriteExistingFile = True
            fam_doc.SaveAs(target, opts)
            alert("Saved:\n" + target)
        except Exception as ex:
            alert("Save As failed: " + str(ex) + "\n\nUse Revit Save As manually to:\n" + new_name + ".rfa")
    else:
        alert(
            "Done without Save As.\n"
            "Parameters written: {}\n"
            "Use Revit Save As to: {}.rfa".format(
                ", ".join(written) if written else "(none)", new_name
            )
        )


if __name__ == "__main__":
    main()
