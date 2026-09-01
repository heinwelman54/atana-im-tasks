# Atana PDOM Phase 2 — Integrated end-state

One model. SA stages primary. IM keeps information execution. DTL stays Accountable. VP is not duplicated.

---

## Output 1 — Validated DTL catalogue

Ownership: **A = DTL**. Information-governance rows stay **R = IM**.

| Code | Task | Stage | Pred | Succ | Type | Verdict |
|---|---|---|---|---|---|---|
| DTL.01.01 | Review Contract | S1 | ZZ-001 | DTL.01.02 | FS | Keep |
| DTL.01.02 | Review Deliverables | S1 | DTL.01.01 | DTL.01.03 | FS | Keep |
| DTL.01.03 | Review Client Requirements | S1 | DTL.01.02 | DTL.02.01 | FS | Keep |
| DTL.01.04 | Manage Variations | S3 | DTL.01.03 | DTL.01.05 | FS | Keep (not a second risk task) |
| DTL.01.05 | Contract Administration | S5 | DTL.01.04 | DTL.10.01 | FS | Keep |
| DTL.02.01 | Complete VP Startup | S1 | DTL.01.03 | DTL.02.02 | FS | Keep — evidence only |
| DTL.02.02 | Project Organisation | S1 | DTL.02.01 | DTL.02.03 | FS | Keep |
| DTL.02.03 | Roles & Responsibilities | S1 | DTL.02.02 | DTL.02.04 | FS | Keep |
| DTL.02.04 | Stakeholder Register | S1 | DTL.02.03 | DTL.02.05 | FS | Keep |
| DTL.02.05 | Communication Plan | S1 | DTL.02.04 | DTL.02.06 | FS | Keep |
| DTL.02.06 | Meeting Structure | S1 | DTL.02.05 | DTL.03.01 | FS | Keep |
| DTL.03.01 | Approve WBS | S1 | DTL.02.06 | DTL.03.02 | FS | Keep |
| DTL.03.02 | Approve Programme | S1 | DTL.03.01 | DTL.03.03 | FS | Keep |
| DTL.03.03 | Approve Resource Plan | S2 | DTL.03.02 | DTL.03.04 | FS | Keep |
| DTL.03.04 | Approve PEP | S2 | DTL.03.03 | DTL.07.01 | FS | Keep |
| DTL.04.01 | Budget Review | S1 | DTL.02.01 | DTL.04.02 | FS | Keep — not VP budget setup |
| DTL.04.02 | Forecast Reviews | S3 | DTL.04.01 | DTL.04.03 | FS | Keep |
| DTL.04.03 | Commercial Reviews | S4 | DTL.04.02 | DTL.04.04 | FS | Keep |
| DTL.04.04 | Invoice Reviews | S5 | DTL.04.03 | DTL.10.01 | FS | Keep |
| DTL.05.01 | Risk Plan | S1 | DTL.02.01 | DTL.05.02 | FS | Keep |
| DTL.05.02 | Risk Register | S2 | DTL.05.01 | DTL.05.03 | SS with PDM production | Create once |
| DTL.05.03 | Opportunity Register | S2 | DTL.05.01 | DTL.05.04 | SS | Keep |
| DTL.05.04 | Lessons Learned Register | S6 | DTL.09.01 | DTL.10.03 | FS | Keep |
| DTL.06.01 | Quality Plan | S1 | DTL.03.04 | DTL.06.02 | FS | Keep |
| DTL.06.02 | Audit Schedule | S3 | DTL.06.01 | DTL.06.03 | FS | Keep |
| DTL.06.03 | Peer Review Schedule | S3 | DTL.06.02 | ZZ-006 | FS | Keep |
| DTL.06.04 | QA Schedule | S3 | DTL.06.02 | ZZ-007 | FS | Keep |
| DTL.07.01 | Approve EIR | S1 | IM.04.01 | DTL.07.02 | FS | A only — IM prepares |
| DTL.07.02 | Approve BEP | S1 | IM.03.01 | DTL.07.03 | FS | A only |
| DTL.07.03 | Approve MIDP | S2 | IM.03.01 | DTL.07.04 | FS | A only |
| DTL.07.04 | Approve Information Standard | S1 | IM.04.01 | DTL.07.05 | FS | A only |
| DTL.07.05 | Approve Information Protocol | S1 | IM.04.01 | ZZ-005 | FS | A only |
| DTL.08.01 | Procurement Plan | S4 | DTL.03.02 | DTL.08.02 | FS | Keep |
| DTL.08.02 | Supplier Review | S4 | DTL.08.01 | DTL.08.03 | FS | Keep |
| DTL.08.03 | Capability Approval | S1 | IM.01.01 | ZZ-003 | FS | Gate owner A |
| DTL.08.04 | Capacity Approval | S1 | IM.01.02 | ZZ-004 | FS | Gate owner A |
| DTL.09.01–04 | Health / Progress / Stakeholder / Client Reviews | S3–S4 | Packages in review | ZZ-008 | FS | Keep |
| DTL.10.01–04 | Closeout Plan / Archive Approval / Lessons / Closure | S6 | ZZ-011 | ZZ-012 | FS | Keep |

No DTL row executes CDE, MIDP authoring, TIDP aggregation, LOIN, IQA, or publish.

---

## Output 2 — Validated PDM catalogue

Ownership: **R = PDM, A = DTL**.

| Code | Task | Stage | Pred | Succ | Type |
|---|---|---|---|---|---|
| PDM.01.01 | Define WBS | S1 | DTL.03.01 | PDM.01.02 | FS |
| PDM.01.02 | Define Production Packages | S1 | PDM.01.01 + IM.03.01 | PDM.01.03 | FS |
| PDM.01.03 | Define Deliverables | S2 | PDM.01.02 | PDM.03.01 | FS |
| PDM.02.01 | Design Strategy | S2 | PDM.01.03 | PDM.02.02 | FS |
| PDM.02.02 | Design Reviews | S3 | PKG production | PDM.02.03 | FS |
| PDM.02.03 | Technical Reviews | S3 | PDM.02.02 | PDM.02.04 | FS |
| PDM.02.04 | Review Resolutions | S3 | PDM.02.03 | ZZ-006 | FS |
| PDM.03.01 | Package Planning | S2 | PDM.01.02 | PDM.03.02 | FS |
| PDM.03.02 | Package Sequencing | S3 | PDM.03.01 | PDM.03.03 | FS |
| PDM.03.03 | Delivery Planning | S3 | PDM.03.02 | PKG start | FS |
| PDM.04.01–03 | Design / Interdiscipline / Package Coordination | S3 | PKG SS across teams | PDM.05.01 | SS / FS |
| PDM.05.01 | Technical QA | S3 | ZZ-006 | ZZ-007 | FS |
| PDM.05.02 | Peer Reviews | S4 | PDM.05.01 | PDM.05.03 | FS |
| PDM.05.03 | Design Checks | S4 | PDM.05.02 | ZZ-009 | FS |
| PDM.06.01–04 | RFIs / Site Queries / Design Changes / Technical Support | S5 | ZZ-010 S4 | S5 packages | FS |

---

## Output 3 — Validated IM catalogue

Ownership: **R = IM, A = DTL**. Do not move these to DTL.

| Code | Task | Stage | Pred | Succ | Type |
|---|---|---|---|---|---|
| IM.01.01 | Capability Assessment | S1 | DTL.02.01 | IM.01.02 | FS |
| IM.01.02 | Capacity Assessment | S1 | IM.01.01 | IM.01.03 | FS |
| IM.01.03 | Mobilisation Plan | S1 | IM.01.02 | IM.01.04 | FS |
| IM.01.04 | Information Readiness Review | S1 | IM.01.03 | ZZ-002 | FS |
| IM.02.01 | CDE Setup | S1 | ZZ-004 | IM.02.02 | FS |
| IM.02.02 | Access Control | S1 | IM.02.01 | IM.02.03 | FS |
| IM.02.03 | Workflow Setup | S1 | IM.02.02 | IM.02.04 | FS |
| IM.02.04 | Archive Setup | S1 | IM.02.03 | ZZ-005 | FS |
| IM.03.01 | Prepare MIDP | S1 | ZZ-005 | DTL.07.03 | FS |
| IM.03.02 | Maintain MIDP | S3 | IM.03.01 | IM.03.04 | FF with packages |
| IM.03.03 | Review TIDPs | S2 | PDM.01.02 | IM.03.04 | FS |
| IM.03.04 | Aggregate TIDPs | S3 | IM.03.03 | IM.03.02 | FS |
| IM.04.01–04 | Information / Naming / Classification Standard, Templates | S1 | IM.01.04 | DTL.07.04 | FS |
| IM.05.01–03 | DPoW Setup, LOIN Definition, Information Requirements | S2–S3 | IM.03.01 | PDM.01.03 | FS |
| IM.06.01–04 | IQA / Information Audits / Metadata Audits / Compliance | S3–S4 | ZZ-006 | ZZ-007 | FS |
| IM.07.01–04 | Federation / Clash / Issues / Model Reviews | S3–S4 | PKG models | ZZ-006 | SS / FS |
| IM.08.01–04 | Publish / Shared / Published / Archive | S4–S6 | ZZ-010 | ZZ-011 | FS |

---

## Output 4 — Missing / duplicate analysis

### Duplicates removed (do not recreate)
| Cluster | Keep | Drop |
|---|---|---|
| Risk | DTL.05.01 Create/Plan, DTL.05.02 Maintain Register | Extra “Risk Review” as its own catalogue row — use DTL.09 reviews |
| MIDP | IM.03.01 Prepare, IM.03.02 Maintain, DTL.07.03 Approve | DTL “Create MIDP” |
| CDE | IM.02.* execute, ZZ-005 gate | DTL “Establish CDE” as execution |
| Quality reviews | PDM.05 + IM.06 + ZZ-006/007 | Second “Design QA” under DTL |
| Closeout lessons | DTL.05.04 register + DTL.10.03 review | Third lessons task |

### Missing DTL (artefacts, not extra owners)
- Change-control log as artefact of DTL.01.04
- Stage-gate recommendation record before ZZ-010

### Missing PDM
- Package owner assignment (field on package, not a new task)
- Intermediate package-type selection (Council / Tender / Construction / As-Built / Handover)

### Missing IM
- Security / information security controls under IM.04 (artefact)
- MIDP revision log (artefact of IM.03.02)

### Missing gates
None. ZZ-001…012 is complete. Do not add RIBA gates.

### Missing registers / artefacts
Stakeholder, opportunity, audit schedule, RFI, published information, archive index — bind to existing tasks.

---

## Output 5 — SA Stage WBS

```
PROJECT
├─ S1 Inception
│  ├─ Governance DTL.01–03, .04.01, .05.01, .06.01, .07, .08.03–04
│  ├─ Governance PDM.01
│  ├─ Governance IM.01–04, IM.03.01
│  ├─ Packages: none (setup)
│  └─ Gates ZZ-001…005, ZZ-010
├─ S2 Concept & Viability
│  ├─ DTL.03.03–04, .05.02–03, .07.03
│  ├─ PDM.01.03, PDM.02.01, PDM.03.01
│  ├─ IM.03.03, IM.05
│  ├─ Production packages (concept set) + Council / Authority types if required
│  ├─ Deliverables: sketches, reports, viability model
│  └─ Gates ZZ-001, 006–010
├─ S3 Design Development
│  ├─ DTL.01.04, .04.02, .06.02–04, .09
│  ├─ PDM.02–05
│  ├─ IM.03.02, IM.03.04, IM.05.03, IM.06, IM.07
│  ├─ Production packages (all active task teams)
│  ├─ Deliverables: coordinated models, GAs, calcs, specs draft
│  └─ Gates ZZ-006–010
├─ S4 Documentation & Procurement
│  ├─ DTL.04.03, .08.01–02, .09.03–04
│  ├─ PDM.05.02–03
│  ├─ IM.06.02, IM.06.04, IM.07.04, IM.08.01–02
│  ├─ Package types: Tender, Permit, Council, Construction issue
│  └─ Gates ZZ-006–010
├─ S5 Construction
│  ├─ DTL.01.05, .04.04
│  ├─ PDM.06
│  ├─ IM.08.03
│  ├─ Package types: Construction, As Built (emerging)
│  └─ Gates ZZ-007–010
└─ S6 Close Out
   ├─ DTL.05.04, DTL.10
   ├─ IM.08.04
   ├─ Package types: As Built, Handover
   └─ Gates ZZ-011, ZZ-012
```

RIBA labels overlay the same WBS. Tasks do not fork.

---

## Output 6 — Gantt dependency matrix (logic)

Default type **FS**. Package-to-package across disciplines **SS** after PDM.03.03. Reviews across disciplines **FF** before ZZ-007.

| Predecessor | Successor | Type | Lag |
|---|---|---|---|
| ZZ-001 | DTL.01.01 | FS | 0 |
| DTL.01.03 | DTL.02.01 | FS | 0 |
| DTL.02.01 | IM.01.01 | FS | 0 |
| IM.01.01 | ZZ-003 | FS | 0 |
| IM.01.02 | ZZ-004 | FS | 0 |
| ZZ-004 | IM.02.01 | FS | 0 |
| IM.02.04 | ZZ-005 | FS | 0 |
| ZZ-005 | IM.03.01 | FS | 0 |
| IM.03.01 | DTL.07.03 | FS | 0 |
| IM.03.01 | PDM.01.02 | FS | 0 |
| PDM.01.02 | PDM.03.01 | FS | 0 |
| PDM.03.03 | PKG (all teams) | FS | 0 |
| PKG AR | PKG ST | SS | 0 |
| PKG ST | PKG ME/EE | SS | 2d |
| PKG + deliverables | ZZ-006 | FS | 0 |
| ZZ-006 | IM.06.01 | FS | 0 |
| IM.06.01 | ZZ-007 | FS | 0 |
| ZZ-007 | ZZ-008 | FS | 0 |
| ZZ-008 | ZZ-009 | FS | 0 |
| ZZ-009 | ZZ-010 | FS | 0 |
| ZZ-010 | IM.08.01 | FS | 0 |
| IM.08.01 | next SA stage ZZ-001 | FS | 0 |
| Council / Authority package | ZZ-009 | FS | 0 |
| Tender package | DTL.08.01 | FF | 0 |
| Construction package | PDM.06 | FS | 0 |
| As Built package | IM.08.04 | FS | 0 |
| Handover package | ZZ-011 | FS | 0 |

Import path: `ATN_TASK_DEPS` in app.html (core spine). Full matrix is this file.

---

## Output 7 — ISO 19650 mapping

| Task / group | Clause | Activity |
|---|---|---|
| DTL.02 / appointment | 19650-2 5.1.1–5.1.2 | Appoint delivery team |
| IM.04 + DTL.07.04 | 5.1.3 | Information standard |
| DTL.07.05 | 5.1.4 | Information protocol |
| IM.01 | 5.1.5–5.1.6 | Capability / capacity / mobilisation |
| IM.02 + ZZ-005 | 5.1.7 | CDE |
| IM.03 + DTL.07.03 | 5.2 / 5.3.2 | MIDP |
| PDM.01 / IM.03.03–04 | 5.3.3 | TIDP / task team planning |
| IM.05 | 19650-1 LOIN | Level of information need |
| PKG production | 5.4 | Generate information |
| IM.06 / ZZ-006–007 | 5.6 / 5.4.5 | Review information |
| IM.08 / ZZ-010 | 5.7 | Deliver / accept information |
| IM.08.04 / DTL.10 | 19650-3 (ops handoff) | Archive / AIM input |

---

## Output 8 — LRQA mapping

| LRQA theme | Tasks / gates | Evidence |
|---|---|---|
| Organisation Structure | DTL.02.02–03 | Org chart, RACI |
| Risk | DTL.05.* | Risk + opportunity registers |
| Process Control | DTL.06, PDM.05, IM.06, ZZ-006–007 | Schedules, IQA, QA |
| Capability | IM.01.01, DTL.08.03, ZZ-003 | Capability assessment |
| Capacity | IM.01.02, DTL.08.04, ZZ-004 | Capacity assessment |
| Mobilisation | IM.01.03–04, DTL.02.01, ZZ-002 | Mobilisation plan, VP evidence |
| Information Management | IM.02–08, DTL.07 | CDE, MIDP, standard, protocol, publish |
| Continuous Improvement | DTL.05.04, DTL.10.03 | Lessons register + review |

---

## Output 9 — PEP mapping

| PEP section | Tasks |
|---|---|
| Scope | DTL.01.02–03, PDM.01 |
| Organisation | DTL.02.02–03 |
| Planning | DTL.03, PDM.03 |
| Financial | DTL.04 |
| QHSE | DTL.06 (quality); H&S remains corporate / VP |
| Risk | DTL.05 |
| Information | DTL.07, IM.* |
| Procurement | DTL.08 |
| Stakeholders | DTL.02.04, DTL.09.03 |
| Communication | DTL.02.05–06 |
| Closeout | DTL.10, IM.08.04, ZZ-011–012 |

---

## Output 10 — BEP mapping

| BEP section | Tasks |
|---|---|
| Appointing Party Requirements | DTL.01.03, DTL.07.01 Approve EIR |
| Project Information Protocol | IM.04 + DTL.07.05 |
| Information Milestones | IM.03, ZZ-009–010 |
| MIDP | IM.03.01–02, DTL.07.03 |
| TIDP | IM.03.03–04, TTM reference |
| CDE | IM.02, ZZ-005 |
| DPoW | IM.05.01 |
| Federation | IM.07.01–02 |
| Issue Management | IM.07.03 |
| Publication | IM.08, ZZ-010 |

---

## Visibility (all roles)

Active role: edit + complete.  
All other DTL / PDM / IM / TTM / TTIM rows: grey, read-only, not completable.

## Package types in the same logic

Design · Council Submission · Authority Submission · Permit Submission · Tender · Construction · As Built · Handover  

Same lifecycle: DEFINED → … → ARCHIVED. They sit between PDM/IM planning and ZZ reviews.
