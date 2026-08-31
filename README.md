# Atana IM

ISO 19650 information-management toolkit.

Open `Atana-IM-Tasks.html` (keep `Atana-IM-Framework.html` in the same folder).
Or use `index.html` / `app.html` as the PWA entry.

**App version 3.6.1** — original single-file IM tool (no TanStack App Builder).
ITE, AIR builder, AIM present-vs-required, Knowledge Graph Engine, and Decide
are inside `Atana-IM-Tasks.html`. See `docs/KGE.md`.

## Workspace tabs (after you open a project)

IM Tasks · Planner · DPoW · MIDP · ITE · AIR · AIM · Graph · Decide · Tools · Documents · WBS

## What 3.6.1 added inside the original tool

| Area | What it does |
| --- | --- |
| **ITE** | Information Template Editor — templates, attributes, LOI |
| **AIR builder** | Asset Information Requirements per asset type; IDS JSON / CSV export |
| **AIM** | Present vs required attributes; 95% completeness gate |
| **Graph** | Operational in-memory graph: Trace, Impact, Ask, Queries, Dashboards, Schema |
| **Decide** | Health, actions, risk, recovery plan, Copilot answers from the same graph |

Parked (not in this file): ACC/SharePoint CDE write-back, live digital twin,
multi-agent AI, executive command center, Neo4j runtime.

## Push to GitHub

```bash
git init
git add .
git commit -m "Atana IM 3.6.1 — original tool + KGE"
git branch -M main
git remote add origin git@github.com:<you>/atana-im.git
git push -u origin main
```

GitHub Pages: enable Pages on `main` / root. `.nojekyll` is included.

## Repo contents

- `Atana-IM-Tasks.html` — operational IM tool + KGE (3.6.1)
- `Atana-IM-Framework.html` — governance brain (roles, CDE, Forma, RACI)
- `app.html` / `index.html` / `manifest.json` / `sw.js` / `icons/` — PWA shell
- `asset-naming-tool.html` + `asset-naming-data.json`
- Schemas and specs: AIM, IRE, DGE, enterprise SQL, JSON schemas, platform docs
- `role-tasks/` — IM, DTL, PDM, TTM, ZZ task packs
- pyRevit: `Atana_Asset_Classify_PyRevit.py`, `Atana_ProjectSync_pyRevit.py`
- `docs/KGE.md` — ontology, queries, impact, production target
