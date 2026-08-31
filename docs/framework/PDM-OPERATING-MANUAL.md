# PDM Operating Manual — Atana Framework v1.0

**Role:** Project Delivery Manager / Design Manager (Design Manager)

**Purpose:** Orchestrate production: scope packages, task teams, interfaces, package approvals and stage-gate recommendation. Sits between Client, DTL, IM and Task Teams.

## Success criteria

- Every Ss package has an owner before PDM-104
- No production before IM-104
- No IM publish before PDM-302
- Stage-gate recommendation is evidence-based

## KPIs

- Packages released vs planned
- Interface issues open
- Package approval lag
- Gate recommendation quality

## Interfaces

DTL, IM, TTM, TTIM, IA, PR, CM

## Escalations

Clash/late/missing information that breaks the sequence; ownership gaps.

## RACI (this seat)

| Task | R | A | C |
|---|---|---|---|
| PDM-000 Prepare to receive the project | PDM | — | DTL |
| PDM-001 Receive project | PDM | — | DTL, IM |
| PDM-002 Review contract requirements | PDM | — | DTL |
| PDM-003A Review client requirements | PDM | — | DTL, IM |
| PDM-003B Review OIR | PDM | — | IM |
| PDM-003C Review PIR | PDM | — | IM |
| PDM-003D Review EIR | PDM | — | IM |
| PDM-003 Create delivery strategy | PDM | DTL | DTL, IM |
| PDM-004 Create design strategy | PDM | DTL | DTL, TTM |
| PDM-005 Establish design governance | PDM | — | DTL, IM |
| PDM-101 Create scope packages | PDM | — | IM, TTM |
| PDM-102 Assign package ownership | PDM | DTL | TTM, DTL |
| PDM-103 Create production plan | PDM | DTL | IM, TTM |
| PDM-104 Release packages for production | PDM | DTL | IM, TTM |
| PDM-105 Identify task teams | PDM | — | DTL |
| PDM-106 Confirm design scope | PDM | — | IM, TTM |
| PDM-107 Review production dependencies | PDM | — | TTM, IM |
| PDM-108 Review delivery risks | PDM | — | DTL |
| PDM-109 Approve production responsibilities | PDM | DTL | DTL, IM |
| PDM-201 Monitor package progress | PDM | — | TTM, IM |
| PDM-202 Coordinate design interfaces | PDM | — | TTM |
| PDM-203 Resolve coordination issues | PDM | — | TTM, IM, DTL |
| PDM-204 Mobilise task teams for concept | PDM | — | TTM, DTL |
| PDM-205 Review concept package readiness | PDM | — | TTM, IM |
| PDM-301 Review package readiness | PDM | — | TTM, IM |
| PDM-302 Approve package | PDM | DTL | IM, DTL |
| PDM-303 Recommend stage gate | PDM | — | IM, DTL |
| PDM-304 Review discipline progress | PDM | — | TTM |
| PDM-305 Review interface risks | PDM | — | TTM |
| PDM-306 Review scope gaps | PDM | — | IM, TTM |
| PDM-307 Review scope overlaps | PDM | — | TTM |
| PDM-308 Review deliverable quality | PDM | — | TTM, IM |
| PDM-309 Review information completeness | PDM | — | IM |
| PDM-310 Review compliance dashboards | PDM | — | IM |
| PDM-401 Issue corrective actions | PDM | — | TTM, IM |
| PDM-402 Re-submit stage gate | PDM | — | IM, DTL |
| PDM-501 Approve design / client submissions | PDM | DTL | IM |
| PDM-502 Approve construction issue packages | PDM | DTL | CM, IM |
| PDM-503 Approve information releases | PDM | — | IM |
| PDM-601 Review design queries / RFIs | PDM | — | TTM, IM, CM |
| PDM-602 Review site changes | PDM | — | CM, DTL |
| PDM-603 Review design deviations | PDM | DTL | TTM, DTL |
| PDM-604 Approve revisions | PDM | DTL | IM, DTL |
| PDM-701 Review handover deliverables | PDM | — | IM, DTL |
| PDM-702 Review AIM readiness | PDM | — | IM |
| PDM-703 Review asset information | PDM | — | IM, FM |
| PDM-704 Approve design completion | PDM | DTL | DTL, IM |

## Task library

### PDM-000 — Prepare to receive the project

- Category: Project Opportunity
- Stage: ST0 Initiate
- Trigger: DTL-009 appointment
- Entry: Appointment letter
- Exit: PDM ready
- Inputs: Appointment
- Outputs: Readiness
- Dependencies: DTL-009
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Ready the PDM seat before DTL-015.
- What next: PDM-001

### PDM-001 — Receive project

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: DTL-015
- Entry: Mobilisation approved
- Exit: Project received on PDM register
- Inputs: Handover, PEP
- Outputs: Received project
- Dependencies: DTL-015
- Consulted: DTL, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Must not start before DTL-015.
- What next: PDM-002

### PDM-002 — Review contract requirements

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Project received
- Entry: Contract
- Exit: Obligations list
- Inputs: Contract
- Outputs: Delivery obligations
- Dependencies: PDM-001
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Extract delivery obligations.
- What next: PDM-003A

### PDM-003A — Review client requirements

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Obligations listed
- Entry: Brief
- Exit: Client requirements note
- Inputs: Brief
- Outputs: Requirements note
- Dependencies: PDM-002
- Consulted: DTL, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Extract design and information needs.
- What next: PDM-003B

### PDM-003B — Review OIR

- Category: Information Management
- Stage: ST0 Initiate
- Trigger: Requirements note
- Entry: OIR
- Exit: OIR implications
- Inputs: OIR
- Outputs: OIR implications
- Dependencies: PDM-003A
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Read organisational information requirements.
- What next: PDM-003C

### PDM-003C — Review PIR

- Category: Information Management
- Stage: ST0 Initiate
- Trigger: OIR reviewed
- Entry: PIR
- Exit: PIR implications
- Inputs: PIR
- Outputs: PIR implications
- Dependencies: PDM-003B
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Read project information requirements.
- What next: PDM-003D

### PDM-003D — Review EIR

- Category: Information Management
- Stage: ST0 Initiate
- Trigger: PIR reviewed
- Entry: EIR
- Exit: EIR implications
- Inputs: EIR
- Outputs: EIR implications
- Dependencies: PDM-003C
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Read exchange information requirements.
- What next: PDM-003

### PDM-003 — Create delivery strategy

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: OIR/PIR/EIR reviewed
- Entry: Strategy draft
- Exit: Delivery strategy issued
- Inputs: OIR, PIR, EIR, Contract
- Outputs: Delivery strategy
- Dependencies: PDM-003D
- Consulted: DTL, IM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 3 / 1
- Why: Predecessor to IM project configuration.
- What next: IM-001 / DTL-014

### PDM-004 — Create design strategy

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Delivery strategy
- Entry: Design strategy draft
- Exit: Design strategy issued
- Inputs: Delivery strategy
- Outputs: Design strategy
- Dependencies: PDM-003
- Consulted: DTL, TTM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Define design management approach.
- What next: PDM-005

### PDM-005 — Establish design governance

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Design strategy
- Entry: Governance draft
- Exit: Design governance live
- Inputs: RACI
- Outputs: Design governance
- Dependencies: PDM-004
- Consulted: DTL, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Set design authority and interfaces.
- What next: PDM-101

### PDM-101 — Create scope packages

- Category: Production Planning
- Stage: ST1 Plan
- Trigger: Delivery strategy approved
- Entry: Package rules
- Exit: Scope Package Register
- Inputs: FB, Ss, Teams
- Outputs: Scope Package Register
- Dependencies: PDM-003
- Consulted: IM, TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 4 / 0
- Why: Packages exist only after this task. Integrates production planning.
- What next: PDM-102 / IM-101

### PDM-102 — Assign package ownership

- Category: Production Planning
- Stage: ST1 Plan
- Trigger: Register exists
- Entry: Team capacity
- Exit: Package owners
- Inputs: Register, Teams
- Outputs: Ownership matrix
- Dependencies: PDM-101
- Consulted: TTM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Assign each package to a task team.
- What next: PDM-103

### PDM-103 — Create production plan

- Category: Production Planning
- Stage: ST1 Plan
- Trigger: Owners assigned
- Entry: Dependencies
- Exit: Production programme
- Inputs: Ownership, Programme envelope
- Outputs: Production plan
- Dependencies: PDM-102
- Consulted: IM, TTM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 4 / 1
- Why: Sequence packages and interfaces.
- What next: PDM-104

### PDM-104 — Release packages for production

- Category: Production Planning
- Stage: ST1 Plan
- Trigger: IM-104 and DTL-102
- Entry: Release checklist
- Exit: Packages released (PLANNED→ready)
- Inputs: MIDP, Production plan
- Outputs: Release record
- Dependencies: IM-104, PDM-103, DTL-102
- Consulted: IM, TTM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: No TTM production before this.
- What next: PKG-REL

### PDM-105 — Identify task teams

- Category: Planning
- Stage: ST1 Plan
- Trigger: Strategy exists
- Entry: Discipline list
- Exit: Task team list
- Inputs: Scope
- Outputs: Task team list
- Dependencies: PDM-003
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm which disciplines are required.
- What next: PDM-102

### PDM-106 — Confirm design scope

- Category: Planning
- Stage: ST1 Plan
- Trigger: Teams listed
- Entry: FB / Ss
- Exit: Confirmed design scope
- Inputs: FB, Ss
- Outputs: Confirmed scope
- Dependencies: PDM-105
- Consulted: IM, TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Confirm FB / systems in and out.
- What next: PDM-101

### PDM-107 — Review production dependencies

- Category: Planning
- Stage: ST1 Plan
- Trigger: Plan drafted
- Entry: Interface list
- Exit: Dependency register
- Inputs: Packages
- Outputs: Dependency register
- Dependencies: PDM-103
- Consulted: TTM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Review package-to-package dependencies.
- What next: PDM-104

### PDM-108 — Review delivery risks

- Category: Risk Management
- Stage: ST1 Plan
- Trigger: Dependencies known
- Entry: Risks
- Exit: Delivery risk register
- Inputs: Plan
- Outputs: Delivery risks
- Dependencies: PDM-107
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Risks to production sequence.
- What next: PDM-201

### PDM-109 — Approve production responsibilities

- Category: Planning
- Stage: ST1 Plan
- Trigger: Owners assigned
- Entry: RACI
- Exit: Responsibilities approved
- Inputs: RACI
- Outputs: Approved responsibilities
- Dependencies: PDM-102
- Consulted: DTL, IM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Lock who produces, reviews, approves.
- What next: PDM-104

### PDM-201 — Monitor package progress

- Category: Production
- Stage: ST2 Concept
- Trigger: Packages released
- Entry: Status feed
- Exit: Progress view
- Inputs: Package status
- Outputs: Progress view
- Dependencies: PDM-104
- Consulted: TTM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: SS with PKG-PRODUCE
- What next: PDM-202

### PDM-202 — Coordinate design interfaces

- Category: Coordination
- Stage: ST2 Concept
- Trigger: Production live
- Entry: Interfaces
- Exit: Interface actions
- Inputs: Dependencies
- Outputs: Interface actions
- Dependencies: PDM-201
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: SS with production.
- What next: PDM-203

### PDM-203 — Resolve coordination issues

- Category: Coordination
- Stage: ST2 Concept
- Trigger: Issue raised
- Entry: Issue
- Exit: Closed issue or escalation
- Inputs: Clash / late / missing
- Outputs: Resolution
- Dependencies: None
- Consulted: TTM, IM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Triggered by clash, late deliverable or missing information.
- What next: DTL-301 if needed

### PDM-204 — Mobilise task teams for concept

- Category: Production
- Stage: ST2 Concept
- Trigger: PDM-104
- Entry: Teams
- Exit: Teams mobilised
- Inputs: Owners
- Outputs: Mobilisation record
- Dependencies: PDM-104
- Consulted: TTM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Stand teams up for concept packages.
- What next: PDM-201

### PDM-205 — Review concept package readiness

- Category: Review
- Stage: ST2 Concept
- Trigger: Concept produced
- Entry: Concept set
- Exit: Readiness note
- Inputs: Concept deliverables
- Outputs: Readiness
- Dependencies: PKG-PRODUCE
- Consulted: TTM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Concept outputs ready for review.
- What next: PDM-301

### PDM-301 — Review package readiness

- Category: Review
- Stage: ST3 Coordinated Design
- Trigger: PKG-TTM
- Entry: TTM approval
- Exit: Readiness reviewed
- Inputs: TTM approval, Deliverables
- Outputs: Readiness review
- Dependencies: PKG-TTM
- Consulted: TTM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: FS after TTM approval.
- What next: PDM-302

### PDM-302 — Approve package

- Category: Approvals
- Stage: ST3 Coordinated Design
- Trigger: Readiness reviewed
- Entry: Review record
- Exit: Package APPROVED
- Inputs: Readiness
- Outputs: Package approval
- Dependencies: PDM-301
- Consulted: IM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Predecessor to IM-401.
- What next: IM-401 / PKG-IM

### PDM-303 — Recommend stage gate

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: All PDM-302 complete
- Entry: Approvals register
- Exit: Gate recommendation
- Inputs: All package approvals
- Outputs: Recommendation
- Dependencies: PDM-302
- Consulted: IM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Recommend gate only when all in-scope packages are approved.
- What next: DTL-401

### PDM-304 — Review discipline progress

- Category: Design Management
- Stage: ST3 Coordinated Design
- Trigger: Production
- Entry: Progress
- Exit: Actions
- Inputs: TIDP
- Outputs: Actions
- Dependencies: PDM-201
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review each task team against the plan.
- What next: PDM-305

### PDM-305 — Review interface risks

- Category: Risk Management
- Stage: ST3 Coordinated Design
- Trigger: Coordination live
- Entry: Risks
- Exit: Updated risks
- Inputs: Interfaces
- Outputs: Updated risks
- Dependencies: PDM-202
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review remaining interface risk.
- What next: PDM-306

### PDM-306 — Review scope gaps

- Category: Design Management
- Stage: ST3 Coordinated Design
- Trigger: Register vs model
- Entry: Gap list
- Exit: Gap actions
- Inputs: Register
- Outputs: Gap actions
- Dependencies: PDM-101
- Consulted: IM, TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Find missing packages or systems.
- What next: PDM-307

### PDM-307 — Review scope overlaps

- Category: Design Management
- Stage: ST3 Coordinated Design
- Trigger: Ownership matrix
- Entry: Overlap list
- Exit: Ownership corrections
- Inputs: Ownership
- Outputs: Corrections
- Dependencies: PDM-102
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Find double-owned scope.
- What next: PDM-308

### PDM-308 — Review deliverable quality

- Category: Review
- Stage: ST3 Coordinated Design
- Trigger: Deliverables issued
- Entry: Samples
- Exit: Quality note
- Inputs: Deliverables
- Outputs: Quality note
- Dependencies: PKG-PRODUCE
- Consulted: TTM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Sample deliverable quality.
- What next: PDM-301

### PDM-309 — Review information completeness

- Category: Information Management
- Stage: ST3 Coordinated Design
- Trigger: IM completeness view
- Entry: IR
- Exit: Completeness note
- Inputs: IM-202
- Outputs: Completeness note
- Dependencies: IM-202
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Completeness vs IR / LOIN.
- What next: PDM-301

### PDM-310 — Review compliance dashboards

- Category: Project Controls
- Stage: ST3 Coordinated Design
- Trigger: Dashboards
- Entry: Compliance
- Exit: Actions
- Inputs: IM-202
- Outputs: Actions
- Dependencies: IM-202
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Read IM compliance.
- What next: PDM-303

### PDM-401 — Issue corrective actions

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: DTL-403
- Entry: Rejection
- Exit: Corrective actions issued
- Inputs: Rejection
- Outputs: Actions
- Dependencies: DTL-403
- Consulted: TTM, IM
- Approver: —
- Mandatory: False
- Duration / lead (days): 2 / 0
- Why: If gate rejected.
- What next: PDM-301

### PDM-402 — Re-submit stage gate

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: Actions closed
- Entry: Updated pack
- Exit: New recommendation
- Inputs: Actions
- Outputs: Updated recommendation
- Dependencies: PDM-401
- Consulted: IM, DTL
- Approver: —
- Mandatory: False
- Duration / lead (days): 2 / 0
- Why: Re-submit after corrections.
- What next: DTL-401

### PDM-501 — Approve design / client submissions

- Category: Issue
- Stage: ST5 Issue
- Trigger: DTL-402
- Entry: Submission pack
- Exit: Submission approved
- Inputs: Pack
- Outputs: Approval
- Dependencies: DTL-402, PDM-302
- Consulted: IM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve what goes to the client.
- What next: DTL-501

### PDM-502 — Approve construction issue packages

- Category: Issue
- Stage: ST5 Issue
- Trigger: Client path clear
- Entry: C-pack
- Exit: C-issue approved
- Inputs: C-pack
- Outputs: Approval
- Dependencies: PDM-501
- Consulted: CM, IM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve C-issue content.
- What next: DTL-502

### PDM-503 — Approve information releases

- Category: Issue
- Stage: ST5 Issue
- Trigger: Containers ready
- Entry: Release list
- Exit: Release approved
- Inputs: IM list
- Outputs: Release approval
- Dependencies: IM-401
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve IM publication set.
- What next: IM-403

### PDM-601 — Review design queries / RFIs

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: RFI
- Entry: RFI
- Exit: Response or escalation
- Inputs: RFI
- Outputs: Response
- Dependencies: None
- Consulted: TTM, IM, CM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Answer or route RFIs.
- What next: PDM-602

### PDM-602 — Review site changes

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Site change
- Entry: Change
- Exit: Instruction
- Inputs: Change
- Outputs: Instruction
- Dependencies: PDM-601
- Consulted: CM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review site-led change.
- What next: PDM-603

### PDM-603 — Review design deviations

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Deviation
- Entry: Deviation
- Exit: Accept / reject
- Inputs: Deviation
- Outputs: Decision
- Dependencies: PDM-602
- Consulted: TTM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Review deviations from issued information.
- What next: PDM-604

### PDM-604 — Approve revisions

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Revision produced
- Entry: Rev pack
- Exit: Revision approved
- Inputs: Rev
- Outputs: Approval
- Dependencies: PKG-PRODUCE
- Consulted: IM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve the revised package.
- What next: IM-602

### PDM-701 — Review handover deliverables

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: S6 stable
- Entry: Handover register
- Exit: Review note
- Inputs: Register
- Outputs: Review
- Dependencies: PDM-302
- Consulted: IM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Review the handover set.
- What next: PDM-702

### PDM-702 — Review AIM readiness

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: IM-702
- Entry: AIM
- Exit: AIM view
- Inputs: AIM
- Outputs: AIM view
- Dependencies: IM-702
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Review AIM with IM.
- What next: PDM-703

### PDM-703 — Review asset information

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: AIM view
- Entry: Assets
- Exit: Asset note
- Inputs: Assets
- Outputs: Asset note
- Dependencies: PDM-702
- Consulted: IM, FM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Review asset-level completeness.
- What next: PDM-704

### PDM-704 — Approve design completion

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Handover reviewed
- Entry: Completion pack
- Exit: Design completion approved
- Inputs: Pack
- Outputs: Approval
- Dependencies: PDM-701, PDM-703
- Consulted: DTL, IM
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve that design delivery is complete.
- What next: DTL-704
