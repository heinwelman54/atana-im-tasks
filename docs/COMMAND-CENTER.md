# Atana Executive Command Center v1.0

**Status:** Implementation-ready module specification  
**Date:** 2026-08-31  
**Product code:** `atana-ecc`  
**Does not redesign engines.** Consumes Requirements, Plan, Compliance, AIM, Graph, Decide, Governance seats, Ecosystem events.

Companions in this repo:

- `Atana-ECC-KPI-Catalogue-v1.json`
- `Atana-ECC-Score-Engine-v1.json`
- `Atana-ECC-API-v1.json`
- `Atana-ECC-Semantic-Model-v1.json`
- `Atana-ECC-Analytics.sql`
- `Atana-Executive-Command-Center-v1.0.docx`
- `Atana-ECC-KPI-Catalogue-v1.0.xlsx`

Runtime target (already chosen): React + Fluent UI · .NET 9 · PostgreSQL · Power BI · Neo4j · Azure OpenAI · Azure AI Search · Azure.

The current HTML tool stays the IM console. The Command Center is a **separate app** that reads the same contracts (`/v1/ask`, `/v1/graph/*`, score views). It does not become a second SoR.

---

## 1. Architecture

```
Personas  →  ECC React (Fluent)  →  APIM
                                  ├─ ECC API (.NET 9) — scores, snapshots, copilot session
                                  ├─ Atana domain API — bindings, AIM, MIDP, conflicts
                                  ├─ GraphQL / Neo4j — why / impact
                                  ├─ Power BI embedded — pixel-perfect + export
                                  └─ Azure OpenAI — Executive Copilot grounded on /v1/ask
Data plane:
  PDS (OLTP) → events → ecc_snapshot_* (OLAP) → Power BI semantic model
```

Single version of the truth = **score views computed from SoR tables**, not numbers typed into a dashboard. Power BI measures must match `ecc.fn_*` formulas. Drift between PBI and ECC API is a defect.

### 1.1 Bounded context

ECC owns: snapshot grain, score versions, watchlists, executive briefings, persona workspace layout.

ECC does **not** own: AIR text, MIDP rows, IDS specs, AIM accept, graph schema. Those stay in existing services.

### 1.2 Screen hierarchy

```
/                    Executive landing (persona default)
/portfolio           Portfolio
/portfolio/{id}/program
/projects            Project list
/projects/{id}       Project command
/projects/{id}/information
/projects/{id}/assets
/projects/{id}/twin
/projects/{id}/risk
/projects/{id}/graph
/insights            AI insights (Decide + Copilot)
/watchlists
/admin/scores        Score version (ORGADMIN)
```

Nav is persona-filtered. An FM never lands on investment performance.

---

## 2. Personas

Each persona has a **home board**, a **KPI strip**, **actions**, **alerts**, **workflow**.

| Persona | Objective | Home | Primary KPIs | Actions | Alert classes |
|---|---|---|---|---|---|
| Executive | Intervene on capital and reputation | Executive | PH portfolio, risk forecast, investment, OIR coverage | Open recovery, call PDM | Portfolio PH < 70, P1 risk |
| Asset Owner | Handover-ready AIM | Asset readiness | AIM%, AIR coverage, handover RAG | Accept/reject AIM (deep-link), demand AIR | Asset RAG red, AIM < gate |
| Client | Appointment information honour | Information | OIR/PIR/EIR coverage | Raise variation (EIR) | EIR unmet at gate |
| Portfolio Manager | Compare projects | Portfolio | #red projects, median IH, reuse | Promote lesson | Cluster of red in a region |
| Program Manager | Programme gate | Portfolio filtered | Programme PH, critical path info | Re-baseline info gate | Programme gate blocked |
| Project Director | One project outcome | Project | PH, stage readiness, P1 count | Gate decision with IM | Gate blocked |
| Project Manager | Time and blockers | Project | DH, blocked packages, forecast delay | Reassign, escalate L2 | Package BLOCKS |
| PDM | Delivery system | Project | TIDP vs MIDP, team load | Lock package | Team overload |
| Information Manager | Honesty of present/required | Information | IH, IDS%, conflicts | Run IDS, resolve conflict | ConflictRecord, IDS fail |
| Construction Manager | Can we build | Project + risk | Stage 5 readiness, missing shop info | Demand package | Missing S5 IR |
| Facility Manager | Can we operate | Asset + twin | Ops readiness, fire-door AIM | Inspection job (CMMS deep-link) | Fire asset red |
| Operations Manager | Live regime | Twin + asset | Twin%, open WO (SoRef), nameplate vs live | Policy opsWins | Telemetry vs AIM conflict |
| Maintenance Manager | Maintainable assets | Asset | PM coverage (SoRef), missing attrs | Create WO | Missing maintain attr |
| Digital Twin Manager | Twin completeness | Twin | Identity, IFC, COBie, DTDL pin | Publish snapshot | Twin id ≠ assetId |

Alerts route through existing events (`gate.blocked`, `aim.completeness.changed`, `conflict.opened`, `decision.raised`) plus ECC-derived `ecc.score.dropped.v1` when a score crosses a band.

---

## 3. Health scoring engine

All scores are **0–100**. Bands: `≥85` Green · `70–84` Amber · `<70` Red. Gate overrides: a project below its **stage gate threshold** is Red on Stage Readiness regardless of other greens.

Grain:

| Score | Grain | Refresh |
|---|---|---|
| Asset Health | asset + loi | on observation |
| AIM / Information / Compliance / Delivery / Twin / Ops / Project | project + stage + as_of | 15 min + on event |
| Portfolio | portfolio + as_of | 15 min |

`loi` from existing `atnLoiForStage`: S1/S2=2, S3=3, S4=4, S5/S6=5.

### 3.1 Atomic ratios (never “feel complete”)

```
AIM_pct        = present_attrs / required_attrs          at loi
IDS_pct        = ids_pass / ids_required
AIR_cov        = air_types_bound_and_active / air_types_required_by_eir
EIR_cov        = eir_satisfied / eir_required
PIR_cov        = pir_satisfied / pir_required
OIR_cov        = oir_satisfied / oir_required
DEL_pub        = published_required_deliverables / required_deliverables
DEL_ontime     = on_time_required / required_deliverables     (due_at <= as_of and published)
PKG_clear      = 1 - blocked_packages / packages
WF_thru        = transitions_forward_7d / transitions_expected_7d   cap 1
RISK_idx       = min(1, (3*P1 + 2*P2 + P3) / risk_norm)             risk_norm default 12
CMMS_bind      = assets_with_external_cmms / assets_in_aim
TWIN_bind      = assets_with_twin_id / assets_in_aim
IFC_pct        = assets_with_ifcguid / assets_in_aim
COBie_pct      = cobie_required_fields_present / cobie_required_fields
IDENT_pct      = assets_with_atana_asset_id_on_element / assets_in_aim
```

`satisfied` for OIR/PIR/EIR = every child requirement at the next layer has a SATISFIES or GENERATES path that is active. Implemented as graph query, cached into `ecc_req_coverage`.

### 3.2 Composite scores

Weights are versioned in `ecc_score_weight` (ORGADMIN). Defaults:

```
InformationHealth IH =
  0.15*OIR_cov + 0.15*PIR_cov + 0.15*EIR_cov
+ 0.20*AIR_cov + 0.20*AIM_pct + 0.15*IDS_pct

ComplianceScore CS = IDS_pct

DeliveryHealth DH =
  0.40*DEL_ontime + 0.30*DEL_pub + 0.30*PKG_clear

AssetHealth AH (per asset) = AIM_pct_asset

ReadinessScore RS (stage) =
  0.50*AIM_pct + 0.30*DEL_pub + 0.20*IDS_pct
  then if RS < project.gate_threshold → band = Red

OperationalReadiness OR =
  0.40*AIM_pct@LOI5 + 0.20*CMMS_bind + 0.20*TWIN_bind + 0.20*DEL_pub_ops
  where DEL_pub_ops = published ops/FM containers / required

DigitalTwinReadiness TR =
  0.25*IDENT_pct + 0.25*IFC_pct + 0.20*COBie_pct + 0.20*AIM_pct + 0.10*TWIN_bind

ProjectHealth PH =
  0.30*IH + 0.25*DH + 0.20*CS + 0.15*(100*(1-RISK_idx)) + 0.10*min(100, 100*WF_thru)

PortfolioHealth PoH =
  sum(PH_i * weight_i) / sum(weight_i)
  weight default = capex_weight if present else 1
```

Aggregation never averages RAG colours. Always average the **numeric** score, then band.

### 3.3 Forecast (Decide, not a new engine)

Delay days predicted:

```
forecast_delay_d =
  0.5 * historical_slip_d_at_this_stage
+ 0.3 * 14 * (1 - RS/100)
+ 0.2 * 7  * P1_open
```

Stored as `ecc_forecast` with model_version. Copilot cites it; it is SoI.

---

## 4. KPI catalogue (canonical names)

Power BI measure names **must** equal these.

| kpi_id | Label | Formula id | Grain | Owner persona |
|---|---|---|---|---|
| ph | Project Health | PH | project | Director / Exec |
| poh | Portfolio Health | PoH | portfolio | Executive / Portfolio |
| ih | Information Health | IH | project | IM / Client |
| cs | Compliance | CS | project | IM |
| dh | Delivery Health | DH | project | PDM / PM |
| rs | Stage Readiness | RS | project+stage | Director |
| ah | Asset Health | AH | asset | AO / FM |
| or | Operational Readiness | OR | project | Ops / FM |
| tr | Twin Readiness | TR | project | Twin manager |
| oir | OIR coverage | OIR_cov | project | Client |
| pir | PIR coverage | PIR_cov | project | Client |
| eir | EIR coverage | EIR_cov | project | Client |
| air | AIR coverage | AIR_cov | project | AO |
| aim | AIM completeness | AIM_pct | project | AO |
| ids | IDS pass | IDS_pct | project | IM |
| gate | Gate threshold | setting | project+stage | IM |
| p1 | Open P1 | count | project | Exec |
| blk | Blocked packages | count | project | PM |
| redn | Red projects | count | portfolio | Portfolio |
| fc_delay | Forecast delay days | forecast | project | PM |

---

## 5. Dashboards

### 5.1 Executive

Strip: PoH, % projects Red, P1 open, forecast delay $ (optional), OIR coverage portfolio.  
Body: portfolio heat map (project × score), risk forecast sparkline, asset readiness donut, investment table (if ERP tag present), OIR coverage by objective.  
Drill: project command.  
Copilot dock: “Which projects require intervention?”

### 5.2 Portfolio

Filters: programme, region, client, stage, task team.  
Matrix: project × (PH, IH, CS, RS, AH, TR).  
Task team performance = mean DH of packages they own.  
Compliance histogram.

### 5.3 Project

Hero PH + band + stage.  
Tiles: IH, DH, CS, RS, AIM%, IDS%, blocked, P1.  
Tabs: deliverables (MIDP state), approvals (workflow), IDS last run, conflicts.  
Action: “Generate recovery plan for this stage” → `/v1/ask`.

### 5.4 Asset readiness

Rows: asset, type, AH, missing attrs, AIR bind, handover RAG, CMMS key, twin key.  
Filter RAG / type / space.

### 5.5 Information

Waterfall OIR→PIR→EIR→AIR→AIM→IDS.  
Completeness by template.  
Unsatisfied parent requirements.

### 5.6 Digital twin

IDENT / IFC / COBie / AIM / bind.  
Assets missing `$dtId` prefix.  
DTDL version vs template version (must match governance pin).

### 5.7 Executive risk

P1/P2/P3, information risks (IDS fail + missing AIR), asset reds, gate risks, forecast delay.  
Source: Decision Engine risks + `ecc_forecast`.

### 5.8 AI insights

Decide actions not accepted, predictions, blocked, recovery opportunities.  
Respect AI classes A–F from the Operating Model. ECC **displays**; it does not auto-apply E/F.

### 5.9 Graph widgets (all boards may embed)

- Why chain (reverse walk)  
- Impact BFS  
- Requirement coverage tree  
- Package BLOCKS subgraph  

Implementation: GraphQL `why(id)`, `impact(id)` already specified. ECC renders as Fluent cards + optional Cytoscape/nvl for network.

---

## 6. Executive Copilot

Same contract as `POST /v1/ask`. ECC adds session, citations UI, and persona prompt prefix.

Grounding order: score snapshot → graph why/impact → named queries → Decide recommendations. No free browse of CDE bytes.

Mapped questions:

| Utterance | Resolver |
|---|---|
| Show all projects at risk | PoH filter PH<70 or P1>0 |
| Which projects are behind schedule | forecast_delay_d > 0 or DEL_ontime < 0.85 |
| Which assets are not operationally ready | AH<gate or OR components missing |
| Top information risks | IDS fail + unsatisfied EIR/AIR |
| What is causing low compliance | group IDS fail by template/attr |
| Recovery plan for Stage 4 | existing `atnAnswer` recover + missing list |
| OIR to AIM traceability | `why` from asset or attr |
| Highest information maturity | max IH |

Citations must show node ids. If the graph cannot answer, say so.

---

## 7. Power BI

### 7.1 Warehouse

Read-only views over `ecc_*` tables (see `Atana-ECC-Analytics.sql`). Import or DirectQuery on Premium; Import for executive strip (15 min).

### 7.2 Star

**Facts:** `fact_project_score`, `fact_asset_score`, `fact_requirement_coverage`, `fact_deliverable_status`, `fact_risk`, `fact_forecast`.

**Dimensions:** `dim_date`, `dim_org`, `dim_portfolio`, `dim_project`, `dim_stage`, `dim_task_team`, `dim_asset_type`, `dim_persona`, `dim_score_version`.

### 7.3 Measures (DAX names = kpi_id)

```
PH = AVERAGE(fact_project_score[ph])
PoH = DIVIDE(SUMX(dim_project, [PH] * dim_project[weight]), SUM(dim_project[weight]))
AIM% = DIVIDE(SUM(fact_asset_score[present]), SUM(fact_asset_score[required]))
Red Projects = CALCULATE(DISTINCTCOUNT(dim_project[project_id]), fact_project_score[ph] < 70)
```

Row-level security: Entra group → `dim_persona` + project membership table `ecc_acl` (same roles as Operating Model).

---

## 8. Backend

### 8.1 Domain

`ScoreSnapshot`, `ScoreWeight`, `Watchlist`, `Briefing`, `CopilotSession`, `AlertSubscription`.

### 8.2 REST (ECC API)

Prefix `/v1/ecc`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/scores/portfolios/{id}` | PoH + children |
| GET | `/scores/projects/{id}` | All project scores |
| GET | `/scores/projects/{id}/assets` | AH list |
| GET | `/kpis` | Catalogue |
| GET | `/snapshots/{id}` | Immutable as_of |
| POST | `/snapshots` | Manual freeze (IM) |
| GET | `/watchlists` | Persona |
| POST | `/ask` | Copilot (wraps /v1/ask + snapshot context) |
| GET | `/graph/why/{nodeId}` | Proxy |
| GET | `/graph/impact/{nodeId}` | Proxy |
| GET | `/insights/projects/{id}` | Open Decide actions |
| GET | `/alerts` | Raised, not accepted |

GraphQL (read): `projectCommand(id)`, `portfolioHeat(id)`, `why`, `impact`.

### 8.3 Events consumed / emitted

Consume: all Atana domain events already specified.  
Emit: `ecc.score.dropped.v1`, `ecc.snapshot.frozen.v1`, `ecc.alert.acknowledged.v1`.

### 8.4 Cache

Redis (or in-proc memory for first ship): score JSON per project 15 min, invalidated on consumed events. Snapshots never cached as mutable.

### 8.5 Security

Entra + existing scopes. ECC adds `atana.ecc.read`, `atana.ecc.watchlist.write`. Field permission: investment measures hidden unless ERP binding + exec/portfolio persona. Audit: briefing export and snapshot freeze use the governance change tuple.

---

## 9. Database (analytics)

OLTP remains PDS. ECC adds schema `ecc`:

- `ecc_score_weight`  
- `ecc_req_coverage`  
- `ecc_project_score`  
- `ecc_asset_score`  
- `ecc_forecast`  
- `ecc_snapshot`  
- `ecc_watchlist`  
- `ecc_alert`  
- `ecc_acl`  
- materialized views `ecc_mv_portfolio`, `ecc_mv_info_waterfall`

Time-series: `ecc_project_score` is append-only (`as_of`). Do not update history.

---

## 10. Widget library

`ScoreHero`, `RagChip`, `KpiStrip`, `HeatMatrix`, `WaterfallReq`, `AssetTable`, `RiskList`, `ForecastSpark`, `GraphWhy`, `GraphImpact`, `CopilotDock`, `ActionQueue`, `GateBanner`.

Layout: 12-col Fluent grid. Executive landing = strip + heat + copilot. Project = hero + 8 tiles + tabs.

Visual language: existing Atana tokens — purple 950/900, gold 500, paper, RAG green `#2f7d5a` / amber gold / danger `#b5442e`.

---

## 11. Implementation roadmap

| Wave | Ship | Exit |
|---|---|---|
| C0 | Score views + formulas in PostgreSQL | `AIM%` in SQL = HTML `atnAimScore` on seed |
| C1 | ECC API scores + one React project page | Director can see PH/IH/AIM/IDS |
| C2 | Portfolio + Executive landing + PBI semantic model | PoH matches API |
| C3 | Asset + Information + Risk boards | Waterfall OIR→AIM |
| C4 | Graph widgets + Copilot dock | “What is blocking Stage 4?” cites graph |
| C5 | Twin + Ops boards | TR components visible even if twin not live |
| C6 | Watchlists, snapshot freeze, RLS in PBI | Audit pack includes frozen scores |

Do not wait for Multi-Agent or a live twin. C5 renders readiness from AIM + identity keys already in the ecosystem contracts.

Parked: writing AIM accept from ECC (deep-link to IM tool / API with AO seat). ECC is a System of Engagement + Intelligence window, not a new SoR.
