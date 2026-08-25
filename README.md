# Atana IM Tasks v3.7.0 — Phase 1 Production Framework

## Phase 1 (scope-driven)

- **Source of truth:** Project Settings → Functional Breakdown (FB), Task Teams (Ro attribute), Phases, Work Stages
- **Production WBS:** FB → Ss (3rd group) → Production Package (`PP-{FB}-{Ss}`)
- **Ro is an attribute**, not a WBS level (grouped only for readability)
- **Packages persist** across all work stages (identity does not restart)
- **Delivery mode:** legacy process task list / Gantt (IM/DTL/PDM/TTM) still available via toggle

## Toggle

IM Planner → **Production (FB→Ss)** | **Delivery (process tasks)**

## Re-sync

WBS → **Re-sync from settings** regenerates packages from current FB × Ss × task team filter (merges existing notes/deps).
