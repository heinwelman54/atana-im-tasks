# -*- coding: utf-8 -*-
"""
Atana Asset Classify + Rename (PyRevit)
Writes Classification.Uniclass Ss / EF / Pr (number + description).
Creates missing shared parameters on the family when possible.
EF is mapped from Pr (product → function hierarchy).
"""

from __future__ import print_function
import os
import json
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import (
    FilteredElementCollector, Family, FamilySymbol,
    StorageType, Transaction, SaveAsOptions,
    ExternalDefinitionCreationOptions, BuiltInCategory,
    Category, SpecTypeId, GroupTypeId, LabelUtils
)
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult, TaskDialogIcon

try:
    from Autodesk.Revit.DB import ForgeTypeId
except Exception:
    ForgeTypeId = None

try:
    from pyrevit import forms
except Exception:
    forms = None

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document if uidoc else None
app = __revit__.Application

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
DATA_CANDIDATES = [
    os.path.join(SCRIPT_DIR, "asset-naming-data.json"),
    os.path.join(SCRIPT_DIR, "..", "asset-naming-data.json"),
    os.path.expandvars(r"%APPDATA%\Atana\asset-naming-data.json"),
]
SP_FILE_CANDIDATES = [
    os.path.join(SCRIPT_DIR, "ATA_ZZ_SharedParameters_MERGED.txt"),
    os.path.join(SCRIPT_DIR, "ATA_ZZ_SharedParameters.txt"),
    os.path.expandvars(r"%APPDATA%\Atana\ATA_ZZ_SharedParameters_MERGED.txt"),
]

PARAM_SS_NUM = "Classification.Uniclass.Ss.Number"
PARAM_SS_DESC = "Classification.Uniclass.Ss.Description"
PARAM_EF_NUM = "Classification.Uniclass.EF.Number"
PARAM_EF_DESC = "Classification.Uniclass.EF.Description"
PARAM_PR_NUM = "Classification.Uniclass.Pr.Number"
PARAM_PR_DESC = "Classification.Uniclass.Pr.Description"

ALL_PARAMS = [PARAM_SS_NUM, PARAM_SS_DESC, PARAM_EF_NUM, PARAM_EF_DESC, PARAM_PR_NUM, PARAM_PR_DESC]

PARAM_GUIDS = {
    PARAM_SS_NUM: "f16eb500-0976-4c80-b5d1-082470821ef8",
    PARAM_SS_DESC: "53e1dbb9-9434-44ad-abcc-51bca479123d",
    PARAM_EF_NUM: "d440faa7-622e-4ee1-9f4e-22a5bedd7074",
    PARAM_EF_DESC: "bcc0bfdd-95e3-4f0f-85b1-ea2260840393",
    PARAM_PR_NUM: "8212e2e8-d020-4127-bada-a9cc7f5f4dcc",
    PARAM_PR_DESC: "d47f96f3-7191-43b2-afc4-db4b5e4a8859",
}


def show_result(title, lines, success=True):
    """Friendly TaskDialog with tick/cross marks."""
    body = []
    for line in lines:
        if not line:
            body.append("")
            continue
        if line.startswith("[OK]"):
            body.append(line.replace("[OK]", "✓", 1))
        elif line.startswith("[NO]"):
            body.append(line.replace("[NO]", "✗", 1))
        elif line.startswith("[..]"):
            body.append(line.replace("[..]", "•", 1))
        else:
            body.append(line)
    msg = "\n".join(body)
    try:
        td = TaskDialog(title)
        td.MainInstruction = title
        td.MainContent = msg
        try:
            td.MainIcon = TaskDialogIcon.TaskDialogIconInformation if success else TaskDialogIcon.TaskDialogIconWarning
        except Exception:
            pass
        td.CommonButtons = TaskDialogCommonButtons.Ok
        td.Show()
    except Exception:
        TaskDialog.Show(title, msg)


def ask_yes_no(instruction, content, title="Atana Asset Classify"):
    try:
        td = TaskDialog(title)
        td.MainInstruction = instruction
        td.MainContent = content
        try:
            td.MainIcon = TaskDialogIcon.TaskDialogIconInformation
        except Exception:
            pass
        td.CommonButtons = TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No
        return td.Show() == TaskDialogResult.Yes
    except Exception:
        r = TaskDialog.Show(title, instruction + "\n\n" + content, TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No)
        return r == TaskDialogResult.Yes


def load_data():
    for p in DATA_CANDIDATES:
        p = os.path.normpath(p)
        if os.path.isfile(p):
            with open(p, "r") as f:
                return json.load(f), p
    return None, None


def find_shared_param_file():
    for p in SP_FILE_CANDIDATES:
        p = os.path.normpath(p)
        if os.path.isfile(p):
            return p
    # current app shared param file if set
    try:
        cur = app.SharedParametersFilename
        if cur and os.path.isfile(cur):
            return cur
    except Exception:
        pass
    return None


def parse_family_name(name):
    if not name:
        return None
    base = os.path.splitext(name)[0]
    parts = base.split("_")
    if len(parts) < 5:
        return None
    return {
        "originator": parts[0],
        "source": parts[1],
        "category": parts[2],
        "material": parts[3],
        "object": "_".join(parts[4:]),
        "full": base,
    }


def ef_from_pr(pr, pr_desc):
    """Map Pr_AA_BB_CC_DD → EF_AA_BB_CC using product hierarchy."""
    if not pr:
        return None, None
    import re
    m = re.match(r"Pr[_\s]?(\d{2})[_\s]?(\d{2})[_\s]?(\d{2})(?:[_\s]?(\d{2}))?", str(pr), re.I)
    if not m:
        return None, None
    a, b, c, d = m.groups()
    ef = "EF_{}_{}_{}".format(a, b, c)
    known = {
        "EF_65_40_33": "General space ventilation",
        "EF_65_40_32": "Fume extraction",
        "EF_65_40_80": "Smoke extraction and control",
        "EF_65_80_12": "Central air conditioning",
        "EF_60_40_37": "Heating",
        "EF_60_40_17": "Cooling",
        "EF_55_70_38": "Hot and cold water supply",
        "EF_25_30_25": "Doors",
        "EF_25_30_97": "Windows",
        "EF_30_20": "Floors",
        "EF_30_10": "Roofs",
        "EF_20_10_30": "Framed structures",
        "EF_20_05_30": "Foundations",
    }
    return ef, known.get(ef) or pr_desc or None


def lookup_classification(data, parts):
    out = {
        "ss": None, "ssDesc": None,
        "ef": None, "efDesc": None,
        "pr": None, "prDesc": None,
        "ifc4": None, "material": None,
    }
    for c in data.get("categories") or []:
        if c.get("isGroup"):
            continue
        if (c.get("code") or "").upper() == (parts["category"] or "").upper():
            out["ss"] = c.get("uniclassSs") or None
            out["ssDesc"] = c.get("uniclassDescription") or c.get("label") or None
            break

    for m in data.get("materials") or []:
        if m.get("isGroup"):
            continue
        if (m.get("code") or "").upper() == (parts["material"] or "").upper():
            out["material"] = m.get("uniclassCode") or None
            break

    obj_name = parts.get("object") or ""
    for team, items in (data.get("objectsByTaskTeam") or {}).items():
        for it in items or []:
            if (it.get("name") or "") == obj_name:
                out["pr"] = it.get("uniclassPr") or None
                out["prDesc"] = it.get("uniclassDescription") or None
                out["ifc4"] = it.get("ifc4") or None
                # EF primarily from Pr
                if it.get("uniclassEf"):
                    out["ef"] = it.get("uniclassEf")
                    out["efDesc"] = it.get("uniclassEfDescription")
                break

    # Always prefer EF derived from Pr code
    ef, efd = ef_from_pr(out.get("pr"), out.get("prDesc"))
    if ef:
        out["ef"] = ef
        if efd:
            out["efDesc"] = efd
    return out


def family_has_param(fam_doc, name):
    try:
        fm = fam_doc.FamilyManager
        for fp in fm.GetParameters():
            if fp.Definition.Name == name:
                return True
    except Exception:
        pass
    for el in FilteredElementCollector(fam_doc).OfClass(FamilySymbol).ToElements():
        if el.LookupParameter(name):
            return True
    return False


def ensure_shared_params(fam_doc):
    """
    Ensure Classification shared parameters exist on the family.
    Tries binding from a shared parameter file using FamilyManager.AddParameter.
    Returns (present_list, created_list, missing_list).
    """
    present = []
    created = []
    missing = []

    for name in ALL_PARAMS:
        if family_has_param(fam_doc, name):
            present.append(name)

    need = [n for n in ALL_PARAMS if n not in present]
    if not need:
        return present, created, missing

    sp_path = find_shared_param_file()
    if not sp_path:
        missing.extend(need)
        return present, created, missing

    try:
        prev = app.SharedParametersFilename
    except Exception:
        prev = None

    t = Transaction(fam_doc, "Atana add classification parameters")
    t.Start()
    try:
        app.SharedParametersFilename = sp_path
        def_file = app.OpenSharedParameterFile()
        if def_file is None:
            t.RollBack()
            missing.extend(need)
            return present, created, missing

        # index definitions by name
        defs = {}
        for group in def_file.Groups:
            for d in group.Definitions:
                defs[d.Name] = d

        fm = fam_doc.FamilyManager
        for name in need:
            ext_def = defs.get(name)
            if ext_def is None:
                missing.append(name)
                continue
            try:
                # type parameter, instance=False
                fm.AddParameter(ext_def, GroupTypeId.IdentityData, False)
                created.append(name)
                present.append(name)
            except Exception:
                try:
                    # older API overload: BuiltInParameterGroup
                    from Autodesk.Revit.DB import BuiltInParameterGroup, ParameterType
                    fm.AddParameter(ext_def, BuiltInParameterGroup.PG_IDENTITY_DATA, False)
                    created.append(name)
                    present.append(name)
                except Exception:
                    missing.append(name)
        t.Commit()
    except Exception:
        if t.HasStarted():
            t.RollBack()
        missing.extend([n for n in need if n not in created])
    finally:
        try:
            if prev:
                app.SharedParametersFilename = prev
        except Exception:
            pass

    return present, created, missing


def set_param_on_element(element, name, value):
    if value is None or value == "":
        return False
    p = element.LookupParameter(name)
    if p is None or p.IsReadOnly:
        return False
    try:
        if p.StorageType == StorageType.String:
            p.Set(str(value))
            return True
    except Exception:
        return False
    return False


def write_classifications(fam_doc, classification):
    written = []
    failed = []
    pairs = [
        (PARAM_SS_NUM, classification.get("ss")),
        (PARAM_SS_DESC, classification.get("ssDesc")),
        (PARAM_EF_NUM, classification.get("ef")),
        (PARAM_EF_DESC, classification.get("efDesc")),
        (PARAM_PR_NUM, classification.get("pr")),
        (PARAM_PR_DESC, classification.get("prDesc")),
    ]
    t = Transaction(fam_doc, "Atana write classification values")
    t.Start()
    try:
        fm = fam_doc.FamilyManager
        for pname, val in pairs:
            if not val:
                continue
            found = None
            for fp in fm.GetParameters():
                if fp.Definition.Name == pname:
                    found = fp
                    break
            if found is not None:
                try:
                    fm.Set(found, str(val))
                    written.append(pname)
                    continue
                except Exception:
                    pass
            # fallback type elements
            ok = False
            for el in FilteredElementCollector(fam_doc).OfClass(FamilySymbol).ToElements():
                if set_param_on_element(el, pname, val):
                    ok = True
            if ok:
                written.append(pname)
            else:
                failed.append(pname)
        t.Commit()
    except Exception as ex:
        if t.HasStarted():
            t.RollBack()
        raise ex
    return written, failed


def rename_family_in_project(proj_doc, old_name, new_name):
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
    except Exception:
        if t.HasStarted():
            t.RollBack()
        raise
    return count


def get_open_documents():
    docs = []
    try:
        for d in app.Documents:
            docs.append(d)
    except Exception:
        if doc:
            docs.append(doc)
    return docs


def main():
    if doc is None:
        show_result("Atana Asset Classify", ["[NO] No active document."], success=False)
        return

    data, data_path = load_data()
    if not data:
        show_result(
            "Atana Asset Classify",
            [
                "[NO] asset-naming-data.json not found",
                "",
                "[..] Place it next to script.py or in %APPDATA%\\Atana\\",
            ],
            success=False,
        )
        return

    current_name = doc.Title
    if current_name.lower().endswith(".rfa"):
        current_name = current_name[:-4]

    clip = ""
    try:
        from System.Windows.Forms import Clipboard
        if Clipboard.ContainsText():
            clip = (Clipboard.GetText() or "").strip()
    except Exception:
        pass

    suggested = current_name
    if clip:
        if clip.startswith("{"):
            try:
                suggested = json.loads(clip).get("name") or current_name
            except Exception:
                suggested = current_name
        elif "_" in clip:
            suggested = clip.split("\n")[0].strip()

    new_name = suggested
    if forms:
        new_name = forms.ask_for_string(
            default=suggested,
            prompt="Family name (Originator_Source_Category_Material_Object)",
            title="Atana Asset Naming",
        )
        if not new_name:
            return
    else:
        if not ask_yes_no("Use this family name?", suggested):
            return
        new_name = suggested

    new_name = os.path.splitext(new_name.strip())[0]
    parts = parse_family_name(new_name)
    if not parts:
        show_result(
            "Invalid name",
            [
                "[NO] Name must match:",
                "[..] Originator_Source_Category_Material_Object",
                "",
                "Got:",
                new_name,
            ],
            success=False,
        )
        return

    classification = lookup_classification(data, parts)
    content = (
        "Name: {full}\n\n"
        "Ss: {ss}\n    {ssDesc}\n\n"
        "EF (from Pr): {ef}\n    {efDesc}\n\n"
        "Pr: {pr}\n    {prDesc}\n\n"
        "Material (not written): {mat}\n"
        "Data: {path}"
    ).format(
        full=parts["full"],
        ss=classification.get("ss") or "—",
        ssDesc=classification.get("ssDesc") or "",
        ef=classification.get("ef") or "—",
        efDesc=classification.get("efDesc") or "",
        pr=classification.get("pr") or "—",
        prDesc=classification.get("prDesc") or "",
        mat=classification.get("material") or "—",
        path=data_path,
    )
    if not ask_yes_no("Apply classification & rename?", content):
        return

    if not doc.IsFamilyDocument:
        try:
            n = rename_family_in_project(doc, current_name, new_name)
            show_result(
                "Project document",
                [
                    "[OK] Renamed {} family element(s)".format(n) if n else "[NO] No matching family to rename",
                    "[..] New name: " + new_name,
                    "",
                    "[..] Open the .rfa family to write Ss / EF / Pr parameters.",
                ],
                success=bool(n),
            )
        except Exception as ex:
            show_result("Rename failed", ["[NO] " + str(ex)], success=False)
        return

    fam_doc = doc
    old_family_name = fam_doc.Title
    if old_family_name.lower().endswith(".rfa"):
        old_family_name = old_family_name[:-4]

    # Ensure parameters exist (create from shared param file if needed)
    present, created, missing = ensure_shared_params(fam_doc)

    try:
        written, failed = write_classifications(fam_doc, classification)
    except Exception as ex:
        show_result("Write failed", ["[NO] " + str(ex)], success=False)
        return

    renamed_docs = []
    for d in get_open_documents():
        if d.IsFamilyDocument:
            continue
        try:
            n = rename_family_in_project(d, old_family_name, new_name)
            if n:
                renamed_docs.append("{} ×{}".format(d.Title, n))
            if old_family_name != current_name:
                n2 = rename_family_in_project(d, current_name, new_name)
                if n2:
                    renamed_docs.append("{} ×{}".format(d.Title, n2))
        except Exception:
            pass

    lines = []
    if created:
        lines.append("[OK] Created parameters:")
        for n in created:
            lines.append("    + " + n)
        lines.append("")
    lines.append("[OK] Values written:" if written else "[NO] No values written")
    for n in written:
        lines.append("    ✓ " + n)
    if failed:
        lines.append("")
        lines.append("[NO] Could not write:")
        for n in failed:
            lines.append("    ✗ " + n)
    if missing:
        lines.append("")
        lines.append("[NO] Missing parameters (add shared param file):")
        for n in missing:
            lines.append("    ✗ " + n)
        lines.append("[..] Place ATA_ZZ_SharedParameters_MERGED.txt next to script.py")
    if renamed_docs:
        lines.append("")
        lines.append("[OK] Renamed in open projects:")
        for r in renamed_docs:
            lines.append("    ✓ " + r)

    lines.append("")
    lines.append("[..] Family name target: {}.rfa".format(new_name))

    show_result("Classification applied", lines, success=bool(written))

    if ask_yes_no("Save family as {}.rfa?".format(new_name), "Overwrite if the file already exists."):
        try:
            path = fam_doc.PathName
            folder = os.path.dirname(path) if path else os.path.expanduser("~\\Documents")
            target = os.path.join(folder, new_name + ".rfa")
            if forms:
                target = forms.save_file(file_ext="rfa", default_name=new_name + ".rfa") or target
            opts = SaveAsOptions()
            opts.OverwriteExistingFile = True
            fam_doc.SaveAs(target, opts)
            show_result("Saved", ["[OK] " + target], success=True)
        except Exception as ex:
            show_result("Save As failed", ["[NO] " + str(ex)], success=False)


if __name__ == "__main__":
    main()
