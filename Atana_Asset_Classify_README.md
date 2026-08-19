# Atana Asset Classify (PyRevit)

## Install
1. Create a PyRevit button folder, e.g.  
   `.../Atana.extension/Atana.tab/Assets.panel/Classify.pushbutton/`
2. Copy into that folder:
   - `Atana_Asset_Classify_PyRevit.py` → rename to `script.py` (PyRevit convention)
   - `asset-naming-data.json` (from the Atana repo / Asset Naming export)
3. Reload PyRevit.

## Workflow
1. In **Atana Asset Naming** tool: build the name → **Copy name**.
2. In Revit: open the **family (.rfa)** (Revit 2025 base preferred).
3. Run **Atana Asset Classify**.
4. Confirm the name (clipboard is suggested).
5. Script:
   - Maps Uniclass **Ss / Ma / Pr** + **IFC4** (+ **EF** when present in data)
   - Writes shared parameters on the family
   - Renames the family in any **open project/template** in the same session
   - Prompts **Save As** `.rfa` under the new name

## Shared parameters
Create/load these on the family (GUIDs can be locked later):

| Parameter | Purpose |
|-----------|---------|
| ATA_ZZ_UniclassSs | System (from Category) |
| ATA_ZZ_UniclassMa | Material |
| ATA_ZZ_UniclassPr | Product / object |
| ATA_ZZ_IFC4 | IFC4 entity/type |
| ATA_ZZ_EF | EF code when mapped |

## Notes
- Project-only session: can rename a loaded family, but open the `.rfa` to write parameters + Save As.
- Keep `asset-naming-data.json` in sync with the web tool (Export data Excel → import, or copy JSON from repo).
