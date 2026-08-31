# Atana Project Delivery Operating System v1.0

One operating model. Engines underneath stay as they are.

```
ROLES → TASKS → PRODUCTION → SCOPE PACKAGES → DELIVERABLES
     → WBS → GANTT → APPROVALS → WORKFLOWS → INFORMATION
```

A user does not ask “what next?”. The seat view plus the next-action line answers it.

## Already live in the PWA (My Role)

| Piece | Where |
|---|---|
| DTL / PDM / IM (+ support seats) task libraries | My Role · My seat |
| Stages 0–7 | My Role |
| Packages inserted between generic tasks | Gold cards |
| Programme WBS + Gantt | My Role · Programme |
| Hard BEFORE dependencies | Programme list |
| Controls KPIs + entry/exit + next action | Panel under My Role (v3.40.12) |
| Executive strip | Command tab (existing ECC) |

## Entity model

FunctionalRole → RoleTask (generic) → ProductionActivity (project) → ScopePackage → DeliverablePackage → Deliverable → InformationRequirement → ApprovalGate

Persisted today: `project.roleWork.status`, `package.idmStatus`, `project.idmPlan`.

## Stage gates (entry / exit)

See `ATN_PDOS_GATES` in app.html. Production is forbidden in WS0 and WS4 (review only). Issue is WS5. Revisions are WS6.

## Dependency catalogue (enforced as programme rules)

DTL mobilisation BEFORE PDM receive  
PDM strategy BEFORE IM setup  
Scope packages BEFORE MIDP  
MIDP approved BEFORE production  
PDM release BEFORE task-team produce  
Peer BEFORE TTIM BEFORE TTM BEFORE PDM BEFORE IM publish  
All package approvals BEFORE stage gate  
AIR BEFORE AIM BEFORE handover

## Controls metrics

Package readiness · Information readiness · Gate readiness · Delivery readiness  
Open TIDP · Tasks done · AIM%

Earned-value hooks later: planned vs approved packages × stage weight. Not cost-loaded in this build.

## Guidance

Role change filters tasks, packages, approvals, next action. DTL sees gates; PDM sees package reviews; IM sees publish discipline.

## Command Center

Existing **Command** tab remains the executive surface. PDOS links to it. Do not duplicate ECC here.
