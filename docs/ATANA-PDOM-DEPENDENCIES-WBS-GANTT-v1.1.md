# Outputs 2–4 — Dependencies, WBS, Gantt

## Dependency chain (every production stage)
```
ZZ-001 Stage Start
 → DTL governance (contract / setup / planning as applicable)
 → PDM scope / package planning
 → IM standards / MIDP / DPoW
 → ZZ-003 Capability Approved + ZZ-004 Capacity Approved (S1)
 → ZZ-005 CDE Operational (S1)
 → Production package (task team)
 → Deliverables (model, drawing, calc, spec, schedule, report, register)
 → ZZ-006 Peer Review
 → IM IQA / metadata
 → ZZ-007 QA Review
 → PDM package acceptance
 → ZZ-008 Client Review
 → ZZ-009 Submission
 → DTL / PDM approval
 → ZZ-010 Approval
 → IM publish / shared / published
```

Finish-to-Start unless noted.
SS allowed: parallel packages (AR ↔ ST ↔ ME) after PDM package release.
Gate dependency: no next SA stage until ZZ-010 for current stage.

## WBS
```
PROJECT
 └─ SA STAGE
     ├─ Governance
     │   ├─ DTL.*
     │   ├─ PDM.*
     │   └─ IM.*
     ├─ Production packages (by task team)
     │   └─ Deliverables
     ├─ Reviews (peer / QA / client)
     └─ ZZ gates
```

Packages sit **between** PDM/IM planning tasks and ZZ review gates. They are not DTL tasks.

## Gantt defaults (working days, adjustable)
| Kind | Duration |
|---|---|
| DTL governance task | 2 |
| PDM / IM planning task | 3 |
| Package production (S2) | 10 |
| Package production (S3) | 15 |
| Package production (S4) | 12 |
| Peer review | 3 |
| QA | 2 |
| Client review | 5 |
| Approval / publish | 2 |
| Gate | 0 (milestone) |

Critical path default:  
DTL.02.01 VP Startup → IM.02 CDE → IM.03 MIDP → PDM.01 Packages → production → ZZ-006 → ZZ-007 → ZZ-010 → IM.08 Publish
