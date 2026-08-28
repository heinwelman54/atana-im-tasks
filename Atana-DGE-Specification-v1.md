# Atana Deliverable Generation Engine — Specification v1.0

## 1. Vision
Generate ISO 19650 information containers from project structure (FB, Ss, spatial, teams, stages), not from a hand-picked drawing list.

## 2. Core Principles
- Classification first (spatial, system, asset, space, document)
- Project settings own labels and numbering
- Task teams inherit a generation model
- One production package per FB + Ss; stages are maturity
- Highest override wins: USER > ASSET > PROJECT > ORG > SYSTEM

## 3–7. Catalogues already in the app
Discipline catalogue, functional roles (IA / PR / TTIM / TTM + DTL PDM IM DM), spatial & functional breakdown, generation models (SPATIAL SYSTEM SITE DOCUMENT SPACE).

## 8–11. Assets, systems, spaces, deliverable taxonomy
Driven by Uniclass Ss / SL / project catalogues. Deliverable type ≠ information container.

## 12–14. Naming, packages, containers
Token titles `{SPATIAL} {DELIVERABLE}` / `{SYSTEM} {DELIVERABLE} - {SPATIAL}`. Packages group stage-gated items. Containers: DRAWING DR, MODEL M3, REPORT RP, CALCULATION CA, SCHEDULE SH, SPECIFICATION SP, DATASHEET DS, REGISTER RG, SCHEMATIC SC.

## 15. Workflow engine
WIP (IA) → Peer review (PR) → Shared → TTM approval → Published (IM/PDM) → Archived.

## 16–20. Responsibility, IR, stages, rules, governance
FRRM authorities O/A/V/R/P. IR types geometry / data / documentation at L1–L4. Configurable stages. Decision rules + dependencies. Admin levels SYS / ORG / PROJECT / TTM.

## 21–26. Implementation surface
Entity list: Project, Spatial, FB, Task team, Role, Space, System, Asset, Package, Deliverable, Container, Stage, Rule, IR, Workflow, Audit.
Physical tables live in `Atana-PDS-PostgreSQL-v1.sql`. JSON companions: DGE, Package, Stage, Decision, Hierarchy, Governance, Containers, IR.
APIs remain the Phase 13 domain list (`/production-packages`, `/tidp`, …). UI: Project setup wizard + Generated MIDP tab + MIDP generator + Governance.
MIDP generation: wizard/settings → evaluate rules → packages → flatten by stage → number by container → assign workflow → persist `project.generatedMidp`.
