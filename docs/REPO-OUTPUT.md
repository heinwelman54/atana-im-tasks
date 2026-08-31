# Repo output

**App version: 3.6.2**  
**Build:** `2026-08-31-ecc-console`  
**File:** `Atana-IM-Tasks.html`

## How to open the new screen

1. Open `Atana-IM-Tasks.html` (keep `Atana-IM-Framework.html` beside it).
2. Open a project (workspace).
3. In the purple segmented bar: **IM Tasks · Planner · DPoW · MIDP · ITE · AIR · AIM · Graph · Decide · Command · Tools · Documents**.
4. Click **Command**.

That is the Executive Command Center console. It uses the same AIM present/required scores and `atnAnswer` graph as Graph and Decide.

## What changed on the app in 3.6.2

| Change | Where |
|---|---|
| New workspace tab **Command** | Segmented bar after **Decide** |
| Persona strip (Executive, Client, Asset Owner, …) | Command tab, top |
| Score tiles: Project Health, Information/AIM, Stage Readiness, Compliance, Delivery, Open gaps | Command tab |
| OIR → PIR → EIR → AIR → AIM → IDS waterfall | Command tab, middle |
| Assets not handover-ready | Command tab |
| Executive Copilot chips + ask box | Command tab, bottom |
| Version string `3.6.2` | `APP_VERSION` in the HTML |

Not in this HTML file (docs / contracts only): Power BI semantic model, `ecc` PostgreSQL schema, portfolio warehouse, live CDE write-back.

## App map (everything already in the tool)

| Tab | Version added | What it is |
|---|---|---|
| IM Tasks / Planner / DPoW / MIDP / Tools / Documents | original | ISO 19650 delivery workspace |
| **ITE** | 3.6.1 | Information templates and attributes |
| **AIR** | 3.6.1 | AIR builder, IDS JSON/CSV export |
| **AIM** | 3.6.1 | Present vs required, 95% Stage 4 gate |
| **Graph** | 3.6.1 | Trace, Impact, Ask, Queries, Dashboards, Schema |
| **Decide** | 3.6.1 | Health, actions, risk, recovery, Copilot |
| **Command** | **3.6.2** | Executive strip on the same scores + copilot |

## Repo documents added this session (not extra tabs)

| Pack | Files |
|---|---|
| Ecosystem | `docs/ECOSYSTEM.md`, `Atana-Ecosystem-Architecture-v1.0.docx`, `Atana-Ecosystem-*-v1.json` |
| Operating model | `docs/OPERATING-MODEL.md`, `Atana-Operating-Model-v1.0.docx`, `Atana-Governance-RACI-v1.0.xlsx` |
| Command Center spec | `docs/COMMAND-CENTER.md`, `Atana-Executive-Command-Center-v1.0.docx`, `Atana-ECC-Analytics.sql`, `Atana-ECC-*-v1.json`, `Atana-ECC-KPI-Catalogue-v1.0.xlsx` |

Download: `atana-im-tasks-FULL-REPO.zip`
