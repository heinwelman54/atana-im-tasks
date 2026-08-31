# DTL Operating Manual — Atana Framework v1.0

**Role:** Delivery Team Lead / Project Manager (Project Manager)

**Purpose:** Own client-facing governance, mobilisation, stage gates, commercial and resource authority. Does not produce packages.

## Success criteria

- Mobilisation approved before anyone configures the project
- Stage gates only after PDM recommendation + IM compliance + all package approvals
- Client always has a single DTL voice

## KPIs

- Time to DTL-015
- Gate cycle time
- Escalations closed < 5 days
- Handover acceptance

## Interfaces

Client, PDM, IM, Commercial, FM

## Escalations

Unresolved PDM/IM conflicts, commercial change, failed stage gate.

## RACI (this seat)

| Task | R | A | C |
|---|---|---|---|
| DTL-000 Assess project opportunity | DTL | Client | PDM, Commercial |
| DTL-001 Accept project handover | DTL | Client | PDM, IM |
| DTL-002 Review contract and appointment | DTL | Client | PDM, Legal |
| DTL-003 Review client requirements | DTL | Client | PDM, IM |
| DTL-004 Confirm budget envelope | DTL | Client | Commercial, PDM |
| DTL-005 Confirm high-level programme | DTL | Client | PDM |
| DTL-006 Review strategic risks | DTL | — | PDM, IM |
| DTL-007 Confirm success criteria | DTL | Client | Client, PDM |
| DTL-008 Create project governance structure | DTL | Client | PDM, IM |
| DTL-009 Appoint PDM | DTL | — | HR, Client |
| DTL-010 Appoint Information Manager | DTL | — | PDM |
| DTL-011 Confirm project team | DTL | — | PDM |
| DTL-012 Allocate resources | DTL | — | PDM |
| DTL-013 Establish communication structure | DTL | — | PDM, IM |
| DTL-014 Approve project execution plan | DTL | Client | PDM, IM |
| DTL-015 Approve mobilisation readiness | DTL | Client | PDM, IM |
| DTL-101 Approve project governance (detailed) | DTL | Client | PDM, IM |
| DTL-102 Approve baseline programme | DTL | Client | PDM, IM |
| DTL-103 Approve resource plan | DTL | Client | PDM |
| DTL-104 Approve delivery strategy | DTL | Client | PDM, IM |
| DTL-105 Approve MIDP | DTL | Client | IM, PDM |
| DTL-106 Review commercial constraints | DTL | — | Commercial, PDM |
| DTL-201 Review progress reports | DTL | — | PDM, IM |
| DTL-202 Monitor task team performance | DTL | — | PDM |
| DTL-203 Manage client communication | DTL | — | PDM |
| DTL-301 Manage escalations | DTL | — | PDM, IM |
| DTL-302 Review change requests | DTL | Client | PDM, Commercial |
| DTL-303 Monitor multi-discipline delivery | DTL | — | PDM |
| DTL-401 Review stage-gate pack | DTL | — | PDM, IM |
| DTL-402 Approve stage gate | DTL | Client | PDM, IM |
| DTL-403 Reject stage gate and return | DTL | — | PDM, IM |
| DTL-501 Approve client issue | DTL | Client | PDM, IM |
| DTL-502 Approve construction issue | DTL | — | PDM, CM |
| DTL-601 Monitor construction information delivery | DTL | — | PDM, IM, CM |
| DTL-602 Review critical site risks | DTL | Client | PDM, CM |
| DTL-603 Approve major site changes | DTL | Client | PDM, CM |
| DTL-604 Manage resource conflicts | DTL | — | PDM |
| DTL-701 Approve handover strategy | DTL | Client | PDM, IM, FM |
| DTL-702 Review asset information readiness | DTL | — | IM, PDM |
| DTL-703 Review final deliverables | DTL | Client | PDM, IM |
| DTL-704 Approve project close-out | DTL | Client | PDM, IM |
| DTL-705 Lessons learned | DTL | — | PDM, IM |
| DTL-706 Performance review | DTL | — | PDM, IM |
| DTL-707 Project closure approval | DTL | Client | Client |
| DTL-708 Archive approval | DTL | — | IM |
| DTL-709 Operations transition | DTL | Client | FM, IM |

## Task library

### DTL-000 — Assess project opportunity

- Category: Project Opportunity
- Stage: ST0 Initiate
- Trigger: Opportunity / tender award
- Entry: Appointment pack available
- Exit: Go / no-go recorded
- Inputs: Appointment, Draft scope, Commercial outline
- Outputs: Opportunity decision
- Dependencies: None
- Consulted: PDM, Commercial
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Stops the delivery team starting a job it cannot deliver.
- What next: DTL-001

### DTL-001 — Accept project handover

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Go decision
- Entry: Opportunity accepted
- Exit: Handover certificate accepted
- Inputs: Handover pack
- Outputs: Accepted handover
- Dependencies: DTL-000
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Creates the legal and delivery start line.
- What next: DTL-002

### DTL-002 — Review contract and appointment

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Handover accepted
- Entry: Contract issued
- Exit: Contract obligations register
- Inputs: Contract, Appointment
- Outputs: Obligations register
- Dependencies: DTL-001
- Consulted: PDM, Legal
- Approver: Client
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Confirm contract obligations that bind DTL, PDM and IM.
- What next: DTL-003

### DTL-003 — Review client requirements

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Contract reviewed
- Entry: Requirements pack
- Exit: Requirements accepted or queried
- Inputs: Brief, OIR extract
- Outputs: Accepted requirements
- Dependencies: DTL-002
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Confirm success criteria, constraints and interfaces.
- What next: DTL-004

### DTL-004 — Confirm budget envelope

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Requirements accepted
- Entry: Budget issued
- Exit: Budget baseline noted
- Inputs: Budget
- Outputs: Budget baseline
- Dependencies: DTL-003
- Consulted: Commercial, PDM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm commercial envelope for delivery.
- What next: DTL-005

### DTL-005 — Confirm high-level programme

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Budget noted
- Entry: Outline programme
- Exit: Programme envelope accepted
- Inputs: Outline programme
- Outputs: Programme envelope
- Dependencies: DTL-004
- Consulted: PDM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Accept outline dates before detailed planning.
- What next: DTL-006

### DTL-006 — Review strategic risks

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Programme envelope
- Entry: Risk workshop
- Exit: Strategic risk register
- Inputs: Risks
- Outputs: Strategic risk register
- Dependencies: DTL-005
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Identify risks that block mobilisation.
- What next: DTL-007

### DTL-007 — Confirm success criteria

- Category: Project Initiation
- Stage: ST0 Initiate
- Trigger: Risks reviewed
- Entry: Criteria drafted
- Exit: Success criteria approved
- Inputs: Requirements
- Outputs: Success criteria
- Dependencies: DTL-006
- Consulted: Client, PDM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Lock measurable success criteria.
- What next: DTL-008

### DTL-008 — Create project governance structure

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Success criteria locked
- Entry: Seats named
- Exit: Governance structure issued
- Inputs: RACI, Organisation
- Outputs: Governance structure
- Dependencies: DTL-007
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Seat DTL, PDM, IM and approval rights.
- What next: DTL-009

### DTL-009 — Appoint PDM

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Governance issued
- Entry: Candidate confirmed
- Exit: PDM appointed
- Inputs: CV / capacity
- Outputs: PDM appointment
- Dependencies: DTL-008
- Consulted: HR, Client
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Appoint the Project Delivery Manager.
- What next: DTL-010

### DTL-010 — Appoint Information Manager

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: PDM appointed
- Entry: Candidate confirmed
- Exit: IM appointed
- Inputs: Capacity
- Outputs: IM appointment
- Dependencies: DTL-009
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Appoint the IM.
- What next: DTL-011

### DTL-011 — Confirm project team

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: IM appointed
- Entry: Team list
- Exit: Team confirmed
- Inputs: Organogram
- Outputs: Confirmed team
- Dependencies: DTL-010
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm remaining delivery leadership.
- What next: DTL-012

### DTL-012 — Allocate resources

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Team confirmed
- Entry: Resource offer
- Exit: Resource allocation
- Inputs: Capacity plan
- Outputs: Resource allocation
- Dependencies: DTL-011
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Allocate leadership time and key resources.
- What next: DTL-013

### DTL-013 — Establish communication structure

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: Resources allocated
- Entry: Comms plan draft
- Exit: Comms structure live
- Inputs: Stakeholders
- Outputs: Comms structure
- Dependencies: DTL-012
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Set reporting and escalation paths.
- What next: DTL-014

### DTL-014 — Approve project execution plan

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: PDM strategy ready
- Entry: PEP submitted
- Exit: PEP approved
- Inputs: PEP, Delivery strategy
- Outputs: Approved PEP
- Dependencies: DTL-013, PDM-003
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 1
- Why: Approve PEP / delivery strategy pack.
- What next: DTL-015

### DTL-015 — Approve mobilisation readiness

- Category: Mobilisation
- Stage: ST0 Initiate
- Trigger: PEP approved
- Entry: Readiness checklist
- Exit: Mobilisation approved (DTL-015)
- Inputs: Checklist
- Outputs: Mobilisation approval
- Dependencies: DTL-014
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Blocks PDM-001 and IM-001.
- What next: PDM-001 / IM-001

### DTL-101 — Approve project governance (detailed)

- Category: Planning
- Stage: ST1 Plan
- Trigger: IM project configured
- Entry: Governance pack
- Exit: Governance approved
- Inputs: Governance pack
- Outputs: Approved governance
- Dependencies: IM-001, PDM-003
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve detailed governance after PDM/IM configuration.
- What next: DTL-102

### DTL-102 — Approve baseline programme

- Category: Planning
- Stage: ST1 Plan
- Trigger: Production plan + MIDP draft
- Entry: Baseline pack
- Exit: Baseline approved
- Inputs: PDM-103, IM-101
- Outputs: Baseline programme
- Dependencies: PDM-103, IM-101
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 1
- Why: Approve the baseline used for controls.
- What next: DTL-103

### DTL-103 — Approve resource plan

- Category: Planning
- Stage: ST1 Plan
- Trigger: Owners assigned
- Entry: Resource plan
- Exit: Resource plan approved
- Inputs: PDM-102
- Outputs: Approved resource plan
- Dependencies: PDM-102
- Consulted: PDM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve task-team capacity.
- What next: DTL-104

### DTL-104 — Approve delivery strategy

- Category: Planning
- Stage: ST1 Plan
- Trigger: PDM strategy
- Entry: Strategy pack
- Exit: Strategy approved
- Inputs: PDM-003
- Outputs: Approved delivery strategy
- Dependencies: PDM-003
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve how design and information will be delivered.
- What next: DTL-105

### DTL-105 — Approve MIDP

- Category: Planning
- Stage: ST1 Plan
- Trigger: IM-104 complete
- Entry: MIDP
- Exit: MIDP approved by DTL
- Inputs: MIDP
- Outputs: Approved MIDP
- Dependencies: IM-104
- Consulted: IM, PDM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve the master information delivery plan.
- What next: DTL-201

### DTL-106 — Review commercial constraints

- Category: Planning
- Stage: ST1 Plan
- Trigger: Baseline in draft
- Entry: Commercial note
- Exit: Constraints logged
- Inputs: Contract
- Outputs: Commercial constraints
- Dependencies: DTL-102
- Consulted: Commercial, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm commercial limits on production.
- What next: DTL-201

### DTL-201 — Review progress reports

- Category: Production
- Stage: ST2 Concept
- Trigger: Concept production started
- Entry: Reports issued
- Exit: Comments issued
- Inputs: Progress reports
- Outputs: DTL comments
- Dependencies: PDM-201
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review PDM/IM progress at concept.
- What next: DTL-202

### DTL-202 — Monitor task team performance

- Category: Production
- Stage: ST2 Concept
- Trigger: Teams mobilised
- Entry: Performance data
- Exit: Actions logged
- Inputs: Resource plan
- Outputs: Performance actions
- Dependencies: DTL-103
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Watch capacity and slippage.
- What next: DTL-203

### DTL-203 — Manage client communication

- Category: Coordination
- Stage: ST2 Concept
- Trigger: Ongoing
- Entry: Comms calendar
- Exit: Record of communication
- Inputs: Comms structure
- Outputs: Client record
- Dependencies: DTL-013
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Keep the appointing party informed.
- What next: DTL-301

### DTL-301 — Manage escalations

- Category: Design Management
- Stage: ST3 Coordinated Design
- Trigger: Escalation raised
- Entry: Issue brief
- Exit: Decision recorded
- Inputs: Issue
- Outputs: Escalation decision
- Dependencies: None
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Handle issues PDM cannot close.
- What next: DTL-302

### DTL-302 — Review change requests

- Category: Design Management
- Stage: ST3 Coordinated Design
- Trigger: Change raised
- Entry: Change pack
- Exit: Change decision
- Inputs: Change
- Outputs: Change decision
- Dependencies: None
- Consulted: PDM, Commercial
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Review changes with commercial impact.
- What next: DTL-303

### DTL-303 — Monitor multi-discipline delivery

- Category: Coordination
- Stage: ST3 Coordinated Design
- Trigger: Packages in production
- Entry: Coordination report
- Exit: Oversight note
- Inputs: PDM-202
- Outputs: Oversight note
- Dependencies: PDM-202
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Confirm PDM is coordinating interfaces.
- What next: DTL-401

### DTL-401 — Review stage-gate pack

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: PDM-303 and IM-303
- Entry: Gate pack
- Exit: Gate pack reviewed
- Inputs: Gate pack
- Outputs: Review record
- Dependencies: PDM-303, IM-303
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Read PDM recommendation and IM compliance.
- What next: DTL-402

### DTL-402 — Approve stage gate

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: All package approvals
- Entry: Gate pack complete
- Exit: Stage gate approved or rejected
- Inputs: All package approvals, IM compliance
- Outputs: Stage gate decision
- Dependencies: DTL-401
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Blocks Stage 5 issue.
- What next: DTL-501 / IM-401

### DTL-403 — Reject stage gate and return

- Category: Approvals
- Stage: ST4 Review & Approval
- Trigger: Gate not ready
- Entry: Findings
- Exit: Rejection with actions
- Inputs: Findings
- Outputs: Corrective actions
- Dependencies: DTL-401
- Consulted: PDM, IM
- Approver: —
- Mandatory: False
- Duration / lead (days): 1 / 0
- Why: Return the stage with corrective actions.
- What next: PDM-303

### DTL-501 — Approve client issue

- Category: Issue
- Stage: ST5 Issue
- Trigger: Stage gate approved
- Entry: Issue pack
- Exit: Client issue approved
- Inputs: Issue pack
- Outputs: Issue approval
- Dependencies: DTL-402, PDM-501
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve information leaving the delivery team.
- What next: IM-401

### DTL-502 — Approve construction issue

- Category: Issue
- Stage: ST5 Issue
- Trigger: Client issue path clear
- Entry: C-issue pack
- Exit: Construction issue approved
- Inputs: C-issue pack
- Outputs: C-issue approval
- Dependencies: DTL-501, PDM-502
- Consulted: PDM, CM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve construction information issue.
- What next: IM-403

### DTL-601 — Monitor construction information delivery

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: On site
- Entry: Revision log
- Exit: Oversight actions
- Inputs: Registers
- Outputs: Oversight actions
- Dependencies: IM-601
- Consulted: PDM, IM, CM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Watch that revisions keep pace with site.
- What next: DTL-602

### DTL-602 — Review critical site risks

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Critical risk
- Entry: Risk note
- Exit: Decision
- Inputs: Risk
- Outputs: Decision
- Dependencies: None
- Consulted: PDM, CM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review risks that threaten safety or programme.
- What next: DTL-603

### DTL-603 — Approve major site changes

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Major change
- Entry: Change pack
- Exit: Approval
- Inputs: Change
- Outputs: Approved change
- Dependencies: PDM-603
- Consulted: PDM, CM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve variations with design impact.
- What next: IM-602

### DTL-604 — Manage resource conflicts

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Conflict flagged
- Entry: Capacity data
- Exit: Allocation decision
- Inputs: Resource plan
- Outputs: Allocation decision
- Dependencies: DTL-103
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Resolve capacity conflicts across teams.
- What next: DTL-701

### DTL-701 — Approve handover strategy

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: S6 complete enough
- Entry: Handover strategy
- Exit: Strategy approved
- Inputs: Strategy
- Outputs: Approved handover strategy
- Dependencies: PDM-701, IM-701
- Consulted: PDM, IM, FM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Approve how AIM and archive will be handed over.
- What next: DTL-702

### DTL-702 — Review asset information readiness

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Strategy approved
- Entry: AIM score
- Exit: Readiness accepted or rejected
- Inputs: AIM, AIR
- Outputs: Readiness view
- Dependencies: IM-702
- Consulted: IM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm AIM readiness with IM.
- What next: DTL-703

### DTL-703 — Review final deliverables

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: AIM reviewed
- Entry: Final register
- Exit: Final deliverables accepted
- Inputs: Registers
- Outputs: Acceptance
- Dependencies: DTL-702
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Accept the handover set.
- What next: DTL-704

### DTL-704 — Approve project close-out

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Deliverables accepted
- Entry: Close-out pack
- Exit: Close-out approved
- Inputs: Close-out pack
- Outputs: Close-out approval
- Dependencies: DTL-703
- Consulted: PDM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Close the delivery appointment.
- What next: DTL-705

### DTL-705 — Lessons learned

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Close-out approved
- Entry: Workshop
- Exit: Lessons record
- Inputs: Issues log
- Outputs: Lessons
- Dependencies: DTL-704
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Capture delivery lessons.
- What next: DTL-706

### DTL-706 — Performance review

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Lessons captured
- Entry: KPIs
- Exit: Performance note
- Inputs: KPIs
- Outputs: Performance note
- Dependencies: DTL-705
- Consulted: PDM, IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Review DTL/PDM/IM performance.
- What next: DTL-707

### DTL-707 — Project closure approval

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Performance reviewed
- Entry: Closure pack
- Exit: Project closed
- Inputs: Pack
- Outputs: Closure
- Dependencies: DTL-706
- Consulted: Client
- Approver: Client
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Formal closure.
- What next: DTL-708

### DTL-708 — Archive approval

- Category: Archive
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Closure approved
- Entry: Archive pack
- Exit: Archive approved
- Inputs: IM-703
- Outputs: Archive approval
- Dependencies: IM-703
- Consulted: IM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Approve IM archive lock.
- What next: DTL-709

### DTL-709 — Operations transition

- Category: Operations Transition
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Archive approved
- Entry: AIM accepted by FM
- Exit: Operations accepted
- Inputs: AIM
- Outputs: Operations acceptance
- Dependencies: DTL-708
- Consulted: FM, IM
- Approver: Client
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Confirm FM / operator has the AIM.
- What next: —
