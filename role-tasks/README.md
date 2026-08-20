# Functional role task lists

Each JSON file is the **default task template** for a functional role.

## Principle
- Allocation is by **functional role**, not individual.
- Staff assigned to a role inherit that role’s tasks.
- Information Authors (IA) may have multiple people on the same role within a task team.
- Cross-role dependencies will reference other role task ids (future: `dependsOnRole`).

## Sources
- ISO 19650 roles & responsibilities
- Atana Information Management Functional Roles & Responsibilities
- Atana high-level responsibility matrix
- BIM Policy / IM Framework (governance)

## Files
| File | Role |
|------|------|
| `DTL-tasks.json` | Delivery Team Lead |
| `PDM-tasks.json` | Project Delivery Manager |
| `TTM-tasks.json` | Task Team Manager (any discipline) |
| `IM-tasks.json` | Information Manager (current app default) |

## Next
- PEER, TTIM, IA, DM templates
- Merge into project WBS with ghost overlay for non-active roles
- Azure Entra ID maps user → functional role seat
