# Atana Functional Role Delivery Framework v1.0

Standard operating model for every project. Independent of project type.

## Files

| File | What |
|---|---|
| `role-tasks/ATANA-FRAMEWORK-v1.json` | Combined DTL + PDM + IM |
| `role-tasks/DTL-framework-v1.json` | DTL task catalogue |
| `role-tasks/PDM-framework-v1.json` | PDM task catalogue |
| `role-tasks/IM-framework-v1.json` | IM task catalogue |
| `DTL-OPERATING-MANUAL.md` | DTL manual |
| `PDM-OPERATING-MANUAL.md` | PDM manual |
| `IM-OPERATING-MANUAL.md` | IM manual |

Counts: DTL 46 · PDM 47 · IM 46 (139 tasks, every row has ID, name, description, category, R/C/A, trigger, entry/exit, inputs/outputs, dependencies, mandatory, duration, lead, why, what next).

## Critical path

DTL-015 → PDM-003 → IM-001 → PDM-101 → IM-101 → IM-104 → PDM-104 → produce → peer → TTIM → TTM → PDM-301 → PDM-302 → IM-401 → DTL-402 → IM-403

## Package integration

- PDM-101 creates the register  
- PDM-104 releases production (after IM-104)  
- Package chain Plan→Release→Produce→Peer→TTIM→TTM→PDM→IM publish→Gate→Issue→Handover  
- IM-401 must not run before PDM-302  

## App

**My Role** loads `ATN_FW` and lists these tasks by stage for the active seat.

## Implementation

PWA now. Next: persist task instances per project (`project.frameworkTasks[taskId].status`) and drive Gantt ES/EF from `suggestedDurationDays` + `dependencies`.
