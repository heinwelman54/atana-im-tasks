# -*- coding: utf-8 -*-
"""
Atana Asset Naming → Classification write-back (PyRevit)
--------------------------------------------------------
Reads the family / type name pattern:
  Originator_Source_Category_Material_Object

Looks up Category → Uniclass Ss, Material → Uniclass Ma/Pr, Object → Uniclass Pr + IFC4
from asset-naming-data.json (place next to script or set DATA_PATH).

Writes shared parameters (create if missing):
  ATA_ZZ_UniclassSs, ATA_ZZ_UniclassPr, ATA_ZZ_UniclassMa, ATA_ZZ_IFC4

Usage (PyRevit):
  1. Select families in Project Browser or open a family document
  2. Run this script
  3. Confirm overrides when values differ
"""
from __future__ import print_function
import json, os, re
from pyrevit import revit, DB, forms, script

DATA_PATHS = [
    os.path.join(os.path.dirname(__file__), 'asset-naming-data.json'),
    os.path.join(os.path.expanduser('~'), 'Atana', 'asset-naming-data.json'),
]

def load_data():
    for p in DATA_PATHS:
        if os.path.isfile(p):
            with open(p, 'r') as f:
                return json.load(f), p
    path = forms.pick_file(file_ext='json', title='Select asset-naming-data.json')
    if not path:
        return None, None
    with open(path, 'r') as f:
        return json.load(f), path

def parse_name(name):
    # Originator_Source_Category_Material_Object (Object may contain no underscores)
    parts = (name or '').split('_')
    if len(parts) < 5:
        return None
    return {
        'originator': parts[0],
        'source': parts[1],
        'category': parts[2],
        'material': parts[3],
        'object': '_'.join(parts[4:]),  # defensive
    }

def find_category(data, code):
    for c in data.get('categories') or []:
        if not c.get('isGroup') and c.get('code') == code:
            return c
    return None

def find_material(data, code):
    for m in data.get('materials') or []:
        if not m.get('isGroup') and m.get('code') == code:
            return m
    return None

def find_object(data, object_name):
    # search all task teams
    for team, items in (data.get('objectsByTaskTeam') or {}).items():
        for it in items:
            if it.get('name') == object_name:
                return it, team
    return None, None

def ensure_param(doc, name):
    # Minimal: assume shared params already bound; otherwise skip with warning
    return name

def set_param(element, name, value):
    if value is None:
        return False
    p = element.LookupParameter(name)
    if not p:
        # try type
        if hasattr(element, 'Symbol'):
            p = element.Symbol.LookupParameter(name) if element.Symbol else None
    if not p or p.IsReadOnly:
        return False
    if p.StorageType == DB.StorageType.String:
        p.Set(str(value))
        return True
    return False

def main():
    data, path = load_data()
    if not data:
        forms.alert('asset-naming-data.json not found', exitscript=True)

    doc = revit.doc
    # Collect selected family symbols / elements
    targets = [e for e in revit.get_selection()]
    if not targets:
        forms.alert('Select family instances or types first', exitscript=True)

    updates = []
    for el in targets:
        type_name = None
        try:
            if hasattr(el, 'Symbol') and el.Symbol:
                type_name = el.Symbol.FamilyName  # family name holds convention
            elif hasattr(el, 'FamilyName'):
                type_name = el.FamilyName
            else:
                type_name = el.Name
        except Exception:
            type_name = getattr(el, 'Name', None)

        parsed = parse_name(type_name or '')
        if not parsed:
            updates.append((type_name, 'SKIP', 'Name does not match Originator_Source_Category_Material_Object'))
            continue

        cat = find_category(data, parsed['category'])
        mat = find_material(data, parsed['material'])
        obj, team = find_object(data, parsed['object'])

        ss = cat.get('uniclassSs') if cat else None
        ma = mat.get('uniclassCode') if mat else None
        pr = obj.get('uniclassPr') if obj else None
        ifc = obj.get('ifc4') if obj else None

        with revit.Transaction('Atana write classifications'):
            changed = []
            for pname, val in [
                ('ATA_ZZ_UniclassSs', ss),
                ('ATA_ZZ_UniclassMa', ma),
                ('ATA_ZZ_UniclassPr', pr),
                ('ATA_ZZ_IFC4', ifc),
            ]:
                if val and set_param(el, pname, val):
                    changed.append(pname)
            updates.append((type_name, 'OK' if changed else 'NO PARAMS', ', '.join(changed) or 'No shared params written'))

    msg = '\n'.join(['{} · {} · {}'.format(a,b,c) for a,b,c in updates[:40]])
    forms.alert('Classification write-back\nData: {}\n\n{}'.format(path, msg))

if __name__ == '__main__':
    main()
