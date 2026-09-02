# ATANA DELIVERY OPERATING MODEL v1.0

**Status: FROZEN for implementation.**  
Do not add tasks. Attach artefacts, registers, packages and mappings to this model.

South African stages are primary. ISO 19650 is inside the tasks. VP is referenced, not copied.  
DTL = Accountable. PDM = Responsible for design delivery. IM = Responsible for information management.

---

## 1. Validation (Workstream 1)

### Ownership — PASS
| Activity | A | R | Must not move |
|---|---|---|---|
| MIDP prepare / maintain | DTL | IM | DTL does not author MIDP |
| TIDP aggregation | DTL | IM | TTM authors TIDP (A=TTM, R=TTIM) |
| CDE setup / access / workflow | DTL | IM | |
| Information protocol / standard | DTL | IM | DTL only approves |
| Information audits / IQA / publish | DTL | IM | |

### Duplicates — CONSOLIDATED
| Cluster | Single pattern |
|---|---|
| Risk | Create plan (DTL.05.01) → Maintain register (DTL.05.02) → Review via DTL.09 |
| Mobilisation | IM.01 plan + DTL.02.01 VP evidence + ZZ-002 |
| Programme | DTL.03.02 Approve · PDM.03 plan/sequence |
| Quality / reviews | PDM.05 + IM.06 + ZZ-006/007. No third DTL “do the review” row |
| Issues | Issue Register object + IM.07.03. Not a second task tree |

### LRQA controls — PRESENT
Capability Assessment, Capacity Assessment, Mobilisation Plan, Information Protocol, Lessons Learned: **in catalogue**.  
Assignment Matrix: **artefact of DTL.02.03** (not a new task).  
BIM Audit: **IM.06 + Audit Register**.  
Continuous Improvement: **DTL.05.04 + DTL.10.03**.

---

## 2. Stages (primary)

| SA | RIBA map |
|---|---|
| 1 Inception | 0–1 |
| 2 Concept & Viability | 2 |
| 3 Design Development | 3 |
| 4 Documentation & Procurement | 4 |
| 5 Construction | 5 |
| 6 Close Out | 6–7 |

Display mode SA / RIBA / Both changes labels only.

---

## 3. Roles

DTL · PDM · IM · TTM · TTIM · IA · (ZZ is not a role)

---

## 4. Tasks

Frozen catalogues: DTL.01–10, PDM.01–06, IM.01–08. See `ATANA-PDOM-PHASE2.md` Outputs 1–3.

---

## 5. Artefact catalogue (Workstream 2)

Tasks **create or approve** artefacts. Artefacts are files / containers.

| ID | Artefact | Created by | Approved by |
|---|---|---|---|
| ART-PEP | PEP | DTL.03.04 | DTL |
| ART-BEP | BEP | IM (+ DTL.07.02 approve) | DTL |
| ART-MIDP | MIDP | IM.03.01 / .02 | DTL.07.03 |
| ART-TIDP | TIDP | TTIM / TTM | IM.03.03–04 |
| ART-WBS | WBS | PDM.01.01 | DTL.03.01 |
| ART-PRG | Programme | PDM.03 | DTL.03.02 |
| ART-MOB | Mobilisation Plan | IM.01.03 | DTL |
| ART-CAPA | Capability Assessment | IM.01.01 | DTL.08.03 |
| ART-CAPC | Capacity Assessment | IM.01.02 | DTL.08.04 |
| ART-IPRO | Information Protocol | IM.04 | DTL.07.05 |
| ART-ISTD | Information Standard | IM.04.01 | DTL.07.04 |
| ART-AMX | Assignment Matrix | DTL.02.03 | DTL |
| ART-COM | Communication Plan | DTL.02.05 | DTL |
| ART-PIM | PIM | IM / production | IM |
| ART-AIM | AIM | IM.08.04 | DTL.10.02 |
| ART-AST | Asset Register | IM / AIM | IM |
| ART-CLO | Closeout Package | DTL.10 + IM.08.04 | DTL |
| ART-EIR | EIR (appointing party) | Client / DTL.07.01 | DTL |

Registers below are objects, not just files.

---

## 6. Register catalogue (Workstream 3)

First-class objects. Many workflows read/write the same register.

| ID | Register | Owner R | Owner A | Linked tasks |
|---|---|---|---|---|
| REG-RISK | Risk Register | PDM | DTL | DTL.05.02 |
| REG-ISS | Issue Register | IM | PDM | IM.07.03 |
| REG-DEC | Decision Register | PDM | DTL | DTL.09 |
| REG-ACT | Action Register | PDM | DTL | DTL.09 / PDM.02.04 |
| REG-CHG | Change Register | PDM | DTL | DTL.01.04 |
| REG-STK | Stakeholder Register | DTL | DTL | DTL.02.04 |
| REG-REV | Review Register | PDM | DTL | PDM.02 / ZZ-006–008 |
| REG-AUD | Audit Register | IM | DTL | IM.06 / DTL.06.02 |
| REG-LL | Lessons Learned Register | DTL | DTL | DTL.05.04 / DTL.10.03 |
| REG-CAP | Capability Register | IM | DTL | IM.01.01 |

---

## 7. Package templates (Workstream 4)

Each template: owner role, default deliverables, review path, submission, approval.

| Template | Owner | Deliverables | Reviews | Submission | Approval |
|---|---|---|---|---|---|
| Architecture | AR TTM | Model, plans, elevations, schedules, specs | Peer → TTIM → PDM | Stage issue | PDM / DTL gate |
| Civil Roads | CV TTM | Layouts, profiles, details, model | same | same | same |
| Civil Earthworks | CV TTM | Plans, sections, volumes | same | same | same |
| Structural | ST TTM | Model, GAs, calcs, schedules | same | same | same |
| Bridge | ST/CV TTM | Model, GAs, details, calcs | same | same | same |
| Mechanical | ME TTM | Schematics → coordinated model → details | same | same | same |
| HVAC | ME TTM | Schematics, plant, model | same | same | same |
| Electrical | EE TTM | Schematics, reticulation, model | same | same | same |
| Public Health | PH TTM | Schematics, layouts, model | same | same | same |
| Fire | FP TTM | Detection / protection drawings, model | same | same | same |
| Security | SE TTM | Layouts, device schedules | same | same | same |
| Process | PR TTM | P&IDs, model, data sheets | same | same | same |

Lifecycle: DEFINED → PLANNED → IN PRODUCTION → READY FOR REVIEW → READY FOR APPROVAL → APPROVED → ISSUED → AS-BUILT → HANDOVER COMPLETE → ARCHIVED.

---

## 8. Submission package types (Workstream 5)

Sit between design packages and ZZ gates.

Council · Environmental · Permit · Planning · Authority Approval · Tender · Construction · Closeout / Handover.

Same dependency: packages + deliverables → ZZ-006…010.

---

## 9. Role matrix (Workstream 6)

| Activity | DTL | PDM | IM | TTM | TTIM | IA |
|---|---|---|---|---|---|---|
| PEP | A/R | C | C | I | I | I |
| EIR approve | A | C | C | I | I | I |
| BEP | A | C | R | I | C | I |
| MIDP | A | C | R | I | I | I |
| TIDP | I | C | C | A | R | I |
| CDE | A | C | R | I | C | I |
| Information standard / protocol | A | C | R | I | C | I |
| DPoW / LOIN | A | C | R | C | C | I |
| Package definition | A | R | C | C | I | I |
| Design production | I | C | I | A | C | R |
| Design review | I | A | C | R | C | I |
| Clash detection | I | C | A | C | R | I |
| IQA / information audit | A | C | R | I | C | I |
| Publish | A | C | R | I | C | I |
| Stage gate ZZ-010 | A | R | C | I | I | I |
| AIM / archive | A | C | R | I | C | I |

---

## 10. Gates

ZZ-001 Stage Start … ZZ-012 Closeout. Milestones, not a role.

---

## 11. Dependencies / Gantt

Spine: ZZ-001 → VP/startup evidence → IM capability/capacity → ZZ-003/004 → CDE → ZZ-005 → MIDP → packages → deliverables → ZZ-006 Peer → IQA → ZZ-007 QA → ZZ-008 Client → ZZ-009 Submission → ZZ-010 Approval → Publish → next stage.

Full matrix: `ATANA-PDOM-PHASE2.md` Output 6.

---

## 12. ISO / LRQA / PEP / BEP

See Phase 2 Outputs 7–10. Not a parallel workflow.

---

## Implementation rule

Next code work binds **tasks → artefacts → registers → packages**.  
It does not grow the task list.
