# Atana Functional Role Work Management Engine v1.0

Start from **role**, never from deliverables.

```
FUNCTIONAL ROLE
  → GENERIC TASKS (ISO 19650 + ISO 9001, every project)
    → PROJECT TASKS
      → SCOPE PACKAGE TASKS (inserted)
        → DELIVERABLE / WORKFLOW TASKS
```

WBS:

```
Project → Lifecycle stage → Functional role → Tasks → Packages → Deliverables
```

## Catalogue

DTL, PDM, IM, DM, TTM, TTIM, IA, PR, CM, RE.

Priority seats that mobilise a job tomorrow: **DTL, PDM, IM**.

## Task phases

Mobilisation · Planning · Production · Review · Approval · Issue · Construction · Handover · Operations · Closeout

## Rules

- Generic tasks always exist once the project exists.
- Package tasks are created from production packages and sit *between* generic review/approval duties.
- Gantt order: TTM verify/approve → PDM review → DTL/client issue.
- Changing role filters tasks, WBS, next action, and the How Atana Works playbook.
- Checking a task persists on `project.roleWork.status`.

## Gantt

Bars are phase-indexed (not yet resource-level CPM). Stage dates from existing DPoW/WBS schedule still apply on IM Tasks / Planner.

## RACI (summary)

| Task class | DTL | PDM | IM | TTM | IA |
|---|---|---|---|---|---|
| Execution strategy | A | R | C | I | I |
| Information strategy | I | A | R | C | I |
| Package production | I | C | C | A | R |
| Stage gate | A | R | C | C | I |

## Implementation in the PWA

Tab **My Role**. Libraries in `ATN_ROLE_TASK_LIB`. JSON templates remain in `role-tasks/` for the older IM Tasks tree.


## v3.40.9
Full DTL 01–07, PDM 01–10, IM 01–09 framework libraries as supplied. WBS is PROJECT → phase → role tasks, with gold package rows under PDM 06 / IM 04 / DTL 04.
\n## v3.40.11 execution model\nProgramme view generates bars from DTL/PDM/IM tasks plus inserted packages. Dependencies listed as BEFORE rules. project.idmPlan persists the generated bars.\n
