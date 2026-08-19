# -*- coding: utf-8 -*-
"""
Atana Asset Classify + Rename (PyRevit)
--------------------------------------
Uses Atana naming: Originator_Source_Category_Material_Object
Writes Autodesk Classification Manager shared parameters:
  Classification.Uniclass.Ss.Number / Description
  Classification.Uniclass.EF.Number / Description
  Classification.Uniclass.Pr.Number / Description
Material is NOT written (display-only in the web tool).

Requires asset-naming-data.json next to this script or in %APPDATA%\Atana\
"""

from __future__ import print_function
import os
import json
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import (
    FilteredElementCollector, Family, FamilySymbol,
    StorageType, Transaction, SaveAsOptions
)
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult

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
    os.path.expandvars(r"%USERPROFILE%\Atana\asset-naming-data.json"),
]

# Official Classification Manager + Atana shared parameter names
PARAM_SS_NUM = "Classification.Uniclass.Ss.Number"
PARAM_SS_DESC = "Classification.Uniclass.Ss.Description"
PARAM_EF_NUM = "Classification.Uniclass.EF.Number"
PARAM_EF_DESC = "Classification.Uniclass.EF.Description"
PARAM_PR_NUM = "Classification.Uniclass.Pr.Number"
PARAM_PR_DESC = "Classification.Uniclass.Pr.Description"

# GUIDs from ATA-SHARED PARAMETERS (for documentation / future binding)
PARAM_GUIDS = {
    PARAM_SS_NUM: "f16eb500-0976-4c80-b5d1-082470821ef8",
    PARAM_SS_DESC: "53e1dbb9-9434-44ad-abcc-51bca479123d",
    PARAM_EF_NUM: "d440faa7-622e-4ee1-9f4e-22a5bedd7074",
    PARAM_EF_DESC: "bcc0bfdd-95e3-4f0f-85b1-ea2260840393",
    PARAM_PR_NUM: "8212e2e8-d020-4127-bada-a9cc7f5f4dcc",
    PARAM_PR_DESC: "d47f96f3-7191-43b2-afc4-db4b5e4a8859",
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


def lookup_classification(data, parts):
    out = {
        "ss": None, "ssDesc": None,
        "ef": None, "efDesc": None,
        "pr": None, "prDesc": None,
        "ifc4": None, "revitCategory": None,
        "material": None,  # display only
    }
    for c in data.get("categories") or []:
        if c.get("isGroup"):
            continue
        if (c.get("code") or "").upper() == (parts["category"] or "").upper():
            out["ss"] = c.get("uniclassSs") or None
            out["ssDesc"] = c.get("uniclassDescription") or c.get("label") or None
            out["ef"] = c.get("uniclassEf") or c.get("ef") or None
            out["efDesc"] = c.get("uniclassEfDescription") or None
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
                out["revitCategory"] = it.get("revitCategory") or None
                if it.get("uniclassEf"):
                    out["ef"] = it.get("uniclassEf")
                return out
    return out


def set_param(element, name, value):
    if value is None or value == "":
        return False
    p = element.LookupParameter(name)
    if p is None:
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
    """Write Ss + EF + Pr number/description only (not material)."""
    written = []
    pairs = [
        (PARAM_SS_NUM, classification.get("ss")),
        (PARAM_SS_DESC, classification.get("ssDesc")),
        (PARAM_EF_NUM, classification.get("ef")),
        (PARAM_EF_DESC, classification.get("efDesc")),
        (PARAM_PR_NUM, classification.get("pr")),
        (PARAM_PR_DESC, classification.get("prDesc")),
    ]
    t = Transaction(fam_doc, "Atana write classification")
    t.Start()
    try:
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
                        if pname not in written:
                            written.append(pname)
                    except Exception:
                        pass
        except Exception:
            pass

        types = FilteredElementCollector(fam_doc).OfClass(FamilySymbol).ToElements()
        for el in types:
            for pname, val in pairs:
                if set_param(el, pname, val):
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
            "Place it next to this script or in %APPDATA%\\Atana\\"
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

    suggested = clip if (clip and "_" in clip) else current_name
    if "\n" in suggested:
        suggested = suggested.split("\n")[0].strip()
    # if clipboard is JSON from Copy classifications
    if suggested.startswith("{"):
        try:
            suggested = json.loads(suggested).get("name") or current_name
        except Exception:
            suggested = current_name

    new_name = suggested
    if forms:
        new_name = forms.ask_for_string(
            default=suggested,
            prompt="Family name (Atana Asset Naming)",
            title="Atana Asset Naming",
        )
        if not new_name:
            return
    else:
        if not ask_yes_no("Use family name:\n\n{}\n\nYes = continue".format(suggested)):
            return
        new_name = suggested

    new_name = os.path.splitext(new_name.strip())[0]
    parts = parse_family_name(new_name)
    if not parts:
        alert("Name must be:\nOriginator_Source_Category_Material_Object\n\nGot:\n" + new_name)
        return

    classification = lookup_classification(data, parts)
    summary = (
        "Name: {full}\n"
        "Ss: {ss} — {ssDesc}\n"
        "EF: {ef} — {efDesc}\n"
        "Pr: {pr} — {prDesc}\n"
        "Material (not written): {mat}\n"
        "IFC4: {ifc}\n"
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
        ifc=classification.get("ifc4") or "—",
        path=data_path,
    )
    if not ask_yes_no(summary + "\n\nApply rename + write Ss/EF/Pr?"):
        return

    fam_doc = doc if doc.IsFamilyDocument else None
    if fam_doc is None:
        try:
            n = rename_family_in_project(doc, current_name, new_name)
            alert("Project document: renamed {} family element(s) to:\n{}\n\nOpen the .rfa to write classification parameters.".format(n, new_name))
        except Exception as ex:
            alert("Project rename failed: " + str(ex))
        return

    old_family_name = fam_doc.Title
    if old_family_name.lower().endswith(".rfa"):
        old_family_name = old_family_name[:-4]

    try:
        written = write_classifications_to_family(fam_doc, classification)
    except Exception as ex:
        alert("Classification write failed: " + str(ex))
        written = []

    renamed_docs = []
    for d in get_open_documents():
        if d.IsFamilyDocument:
            continue
        try:
            n = rename_family_in_project(d, old_family_name, new_name)
            if n:
                renamed_docs.append("{} ({})".format(d.Title, n))
            if old_family_name != current_name:
                n2 = rename_family_in_project(d, current_name, new_name)
                if n2:
                    renamed_docs.append("{} ({})".format(d.Title, n2))
        except Exception:
            pass

    save_msg = "Parameters written:\n{}\n".format("\n".join(written) if written else "(none — load Classification shared params into the family)")
    if renamed_docs:
        save_msg += "\nRenamed in: {}\n".format(", ".join(renamed_docs))
    save_msg += "\nSave family as:\n{}.rfa ?".format(new_name)

    if ask_yes_no(save_msg):
        try:
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
            alert("Save As failed: " + str(ex))
    else:
        alert("Done without Save As.\nWritten: " + (", ".join(written) if written else "none"))


if __name__ == "__main__":
    main()
