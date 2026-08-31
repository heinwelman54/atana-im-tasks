# Atana IM

ISO 19650 information-management tool.

Open `Atana-IM-Tasks.html` (keep `Atana-IM-Framework.html` in the same folder).
Or use `index.html` / `app.html` as the PWA entry.

**App version 3.40.3 (GitHub Pages `app.html`) / 3.6.2 (`Atana-IM-Tasks.html`)** — 3.6.1 engines plus **Command** tab. Open a project → segmented bar → **Command**. See `docs/REPO-OUTPUT.md`.

**Ecosystem architecture v1.0** — how information flows across CDE, authoring, M365, ERP, CMMS and twins. See `docs/ECOSYSTEM.md` and `Atana-Ecosystem-Architecture-v1.0.docx`. Contracts: `Atana-Ecosystem-*-v1.json`. Not implemented as live write-back in the HTML tool.

**Operating model v1.0** — who owns each object and how the organisation runs Atana. See `docs/OPERATING-MODEL.md`, `Atana-Operating-Model-v1.0.docx`, `Atana-Governance-RACI-v1.0.xlsx`, `Atana-Governance-Objects-v1.json`.

**Executive Command Center v1.0** — consumer app (React + Fluent), not a new SoR. See `docs/COMMAND-CENTER.md`, `Atana-Executive-Command-Center-v1.0.docx`, `Atana-ECC-Analytics.sql`, `Atana-ECC-*-v1.json`, `Atana-ECC-KPI-Catalogue-v1.0.xlsx`.

Live site tabs after you open a project: IM Tasks, Planner, How Atana Works, DPoW, MIDP, ITE, AIR, AIM, Graph, Decide, Command, Tools, Documents, Models.

## Push to GitHub

```bash
git remote add origin git@github.com:<you>/atana-im.git
git push -u origin main
```

## Notes

# Atana IM Tasks v3.5.2
Fixed Project Sync IronPython string syntax errors
