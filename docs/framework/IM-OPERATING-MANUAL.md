# IM Operating Manual — Atana Framework v1.0

**Role:** Information Manager (ISO 19650 Information Manager)

**Purpose:** Own the information environment, MIDP/TIDP, standards, compliance, publication and archive. Does not approve design content.

## Success criteria

- Spatial is per FB
- MIDP exists before production
- Nothing published before PDM-302
- AIR before AIM before archive

## KPIs

- MIDP completeness
- Open TIDP
- Publish lag after PDM-302
- AIM%
- AIR gaps

## Interfaces

DTL, PDM, DM, TTIM, FM

## Escalations

Standards breaches, overdue containers, AIM below gate.

## RACI (this seat)

| Task | R | A | C |
|---|---|---|---|
| IM-000 Prepare information environment | IM | — | DTL |
| IM-001 Configure project | IM | — | PDM, DM |
| IM-002 Setup functional breakdown | IM | — | PDM |
| IM-003 Setup spatial breakdown | IM | — | PDM |
| IM-004 Setup task teams | IM | — | PDM, DTL |
| IM-005 Configure information standards | IM | — | DM |
| IM-006 Configure templates | IM | — | TTIM |
| IM-007 Configure workflows | IM | — | PDM, DM |
| IM-101 Create MIDP | IM | — | PDM, TTM |
| IM-102 Create TIDPs | IM | — | TTM, TTIM |
| IM-103 Configure workflows against MIDP | IM | — | DM |
| IM-104 MIDP approval (IM complete) | IM | DTL | PDM, DTL |
| IM-105 Configure information requirements | IM | — | PDM |
| IM-106 Configure information templates on packages | IM | — | TTIM |
| IM-107 Configure scope packages in the CDE | IM | — | DM, PDM |
| IM-108 Manage classification | IM | — | TTIM |
| IM-109 Manage naming conventions | IM | — | DM |
| IM-110 Manage numbering | IM | — | DM |
| IM-111 Manage metadata | IM | — | TTIM |
| IM-201 Monitor information production | IM | — | TTM, TTIM |
| IM-202 Monitor compliance | IM | — | TTIM, PDM |
| IM-203 Monitor deliverables | IM | — | TTM |
| IM-204 Monitor information completeness | IM | — | PDM |
| IM-205 Monitor workflows | IM | — | DM |
| IM-301 Review metadata | IM | — | TTIM |
| IM-302 Validate information | IM | — | TTIM, PDM |
| IM-303 Validate readiness / compliance confirmation | IM | — | PDM, DTL |
| IM-304 Review classification on containers | IM | — | TTIM |
| IM-305 Review information quality | IM | — | TTM |
| IM-306 Route approvals | IM | PDM | PDM, TTM |
| IM-307 Manage information state changes | IM | — | DM |
| IM-308 Manage escalations (information) | IM | DTL | PDM, DTL |
| IM-401 Publish information | IM | — | PDM, DM |
| IM-402 Update registers | IM | — | DM |
| IM-403 Issue information containers | IM | — | PDM, DM |
| IM-404 Manage shared information | IM | — | DM |
| IM-601 Manage revisions | IM | — | PDM, DM |
| IM-602 Manage updated packages | IM | — | PDM |
| IM-603 Manage construction information exchanges | IM | — | CM, PDM |
| IM-701 Review AIM | IM | — | PDM, FM |
| IM-702 Review AIR compliance | IM | — | PDM |
| IM-703 Prepare handover and archive packages | IM | — | DM, PDM |
| IM-704 Archive information | IM | — | DM |
| IM-705 Lock information records | IM | — | DM |
| IM-706 Generate final registers | IM | — | PDM |
| IM-707 Support lessons learned | IM | — | DTL |

## Task library

### IM-000 — Prepare information environment

- Category: Project Opportunity
- Stage: ST0 Initiate
- Trigger: DTL-010 appointment
- Entry: Access
- Exit: IM ready
- Inputs: Appointment
- Outputs: Readiness
- Dependencies: DTL-010
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Ready CDE/project before DTL-015.
- What next: IM-001

### IM-001 — Configure project

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: DTL-015
- Entry: Mobilisation approved
- Exit: Project record live
- Inputs: PEP, Codes
- Outputs: Configured project
- Dependencies: DTL-015, PDM-003
- Consulted: PDM, DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: No configuration before DTL-015.
- What next: IM-002

### IM-002 — Setup functional breakdown

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: Project configured
- Entry: FB list
- Exit: FB live
- Inputs: Scope
- Outputs: FB
- Dependencies: IM-001
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Configure FBs for the project.
- What next: IM-003

### IM-003 — Setup spatial breakdown

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: FBs live
- Entry: Levels
- Exit: Spatial per FB
- Inputs: Levels
- Outputs: fbSpatial
- Dependencies: IM-002
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Configure spatial per FB (not one list for the project).
- What next: IM-004

### IM-004 — Setup task teams

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: Spatials set
- Entry: Role catalogue
- Exit: Teams live
- Inputs: Roles
- Outputs: Teams
- Dependencies: IM-003
- Consulted: PDM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Activate task teams / roles.
- What next: IM-005

### IM-005 — Configure information standards

- Category: Information Governance
- Stage: ST0 Initiate
- Trigger: Teams live
- Entry: Standards pack
- Exit: Standards live
- Inputs: Standards
- Outputs: Standards
- Dependencies: IM-004
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Naming, numbering, metadata, classification.
- What next: IM-006

### IM-006 — Configure templates

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: Standards live
- Entry: Templates
- Exit: Templates live
- Inputs: ITE
- Outputs: Templates
- Dependencies: IM-005
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Information templates bound to AIR.
- What next: IM-007

### IM-007 — Configure workflows

- Category: Information Mobilisation
- Stage: ST0 Initiate
- Trigger: Templates live
- Entry: Workflow spec
- Exit: Workflows live
- Inputs: States
- Outputs: Workflows
- Dependencies: IM-006
- Consulted: PDM, DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: WIP / Shared / Published / gates.
- What next: IM-101

### IM-101 — Create MIDP

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: Scope Package Register
- Entry: Packages
- Exit: MIDP draft
- Inputs: PDM-101
- Outputs: MIDP draft
- Dependencies: PDM-101
- Consulted: PDM, TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 4 / 1
- Why: Create MIDP from packages and stages. FS after PDM-101.
- What next: IM-102

### IM-102 — Create TIDPs

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: MIDP draft
- Entry: MIDP
- Exit: TIDPs
- Inputs: MIDP
- Outputs: TIDPs
- Dependencies: IM-101
- Consulted: TTM, TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Create task-team plans from MIDP.
- What next: IM-103

### IM-103 — Configure workflows against MIDP

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: MIDP in development
- Entry: MIDP
- Exit: Workflows aligned
- Inputs: MIDP
- Outputs: Aligned workflows
- Dependencies: IM-101
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: SS with MIDP development.
- What next: IM-104

### IM-104 — MIDP approval (IM complete)

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: MIDP complete
- Entry: MIDP
- Exit: MIDP complete record
- Inputs: MIDP
- Outputs: MIDP complete
- Dependencies: IM-101, IM-102
- Consulted: PDM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Blocks PDM-104 production release.
- What next: PDM-104 / DTL-105

### IM-105 — Configure information requirements

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: Packages exist
- Entry: AIR
- Exit: IR bound
- Inputs: AIR, Packages
- Outputs: Bound IR
- Dependencies: PDM-101
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Bind IR / AIR to packages.
- What next: IM-106

### IM-106 — Configure information templates on packages

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: IR bound
- Entry: Templates
- Exit: Templates on packages
- Inputs: ITE
- Outputs: Bound templates
- Dependencies: IM-105
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Bind templates to packages.
- What next: IM-107

### IM-107 — Configure scope packages in the CDE

- Category: Information Planning
- Stage: ST1 Plan
- Trigger: Templates bound
- Entry: CDE
- Exit: Package containers
- Inputs: Packages
- Outputs: Containers
- Dependencies: IM-106
- Consulted: DM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Containers for each package.
- What next: IM-108

### IM-108 — Manage classification

- Category: Information Governance
- Stage: ST1 Plan
- Trigger: Standards live
- Entry: Tables
- Exit: Classification live
- Inputs: Uniclass
- Outputs: Classification
- Dependencies: IM-005
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Uniclass / project classification live.
- What next: IM-109

### IM-109 — Manage naming conventions

- Category: Information Governance
- Stage: ST1 Plan
- Trigger: Classification live
- Entry: Convention
- Exit: Naming live
- Inputs: Convention
- Outputs: Naming
- Dependencies: IM-108
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Apply naming to containers.
- What next: IM-110

### IM-110 — Manage numbering

- Category: Information Governance
- Stage: ST1 Plan
- Trigger: Naming live
- Entry: Series
- Exit: Numbering live
- Inputs: Series
- Outputs: Numbering
- Dependencies: IM-109
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Document / model numbering bands.
- What next: IM-111

### IM-111 — Manage metadata

- Category: Information Governance
- Stage: ST1 Plan
- Trigger: Numbering live
- Entry: Schema
- Exit: Metadata live
- Inputs: Schema
- Outputs: Metadata schema
- Dependencies: IM-110
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Required metadata set.
- What next: IM-201

### IM-201 — Monitor information production

- Category: Information Production Support
- Stage: ST2 Concept
- Trigger: PDM-104
- Entry: Production feed
- Exit: Production watch
- Inputs: TIDP
- Outputs: Watch
- Dependencies: PDM-104
- Consulted: TTM, TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: SS with package production.
- What next: IM-202

### IM-202 — Monitor compliance

- Category: Information Production Support
- Stage: ST2 Concept
- Trigger: Production
- Entry: Rules
- Exit: Compliance view
- Inputs: IDS, IR
- Outputs: Compliance view
- Dependencies: IM-201
- Consulted: TTIM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: SS with production.
- What next: IM-203

### IM-203 — Monitor deliverables

- Category: Information Production Support
- Stage: ST2 Concept
- Trigger: Production
- Entry: Register
- Exit: Deliverable watch
- Inputs: Register
- Outputs: Watch
- Dependencies: IM-201
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Watch deliverable creation.
- What next: IM-204

### IM-204 — Monitor information completeness

- Category: Information Production Support
- Stage: ST2 Concept
- Trigger: Deliverables moving
- Entry: LOIN
- Exit: Completeness view
- Inputs: LOIN
- Outputs: Completeness
- Dependencies: IM-203
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Completeness vs LOIN / stage.
- What next: IM-205

### IM-205 — Monitor workflows

- Category: Information Production Support
- Stage: ST2 Concept
- Trigger: Workflows live
- Entry: States
- Exit: Workflow watch
- Inputs: CDE states
- Outputs: Watch
- Dependencies: IM-007
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: State changes.
- What next: IM-301

### IM-301 — Review metadata

- Category: Information Validation
- Stage: ST3 Coordinated Design
- Trigger: PKG-PEER
- Entry: Containers
- Exit: Metadata reviewed
- Inputs: Peer complete
- Outputs: Metadata review
- Dependencies: PKG-PEER
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: FS after peer review complete.
- What next: IM-302

### IM-302 — Validate information

- Category: Information Validation
- Stage: ST3 Coordinated Design
- Trigger: PKG-TTIM
- Entry: Containers
- Exit: Information validated
- Inputs: TTIM
- Outputs: Validation
- Dependencies: PKG-TTIM
- Consulted: TTIM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: FS after TTIM review.
- What next: IM-303

### IM-303 — Validate readiness / compliance confirmation

- Category: Information Validation
- Stage: ST4 Review & Approval
- Trigger: PDM-302
- Entry: Approvals
- Exit: IM compliance confirmation
- Inputs: Approvals
- Outputs: Compliance confirmation
- Dependencies: PDM-302
- Consulted: PDM, DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: For DTL gate.
- What next: DTL-401

### IM-304 — Review classification on containers

- Category: Information Validation
- Stage: ST3 Coordinated Design
- Trigger: Containers submitted
- Entry: Class
- Exit: Class review
- Inputs: Class
- Outputs: Review
- Dependencies: IM-108
- Consulted: TTIM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Classification still correct.
- What next: IM-302

### IM-305 — Review information quality

- Category: Information Validation
- Stage: ST3 Coordinated Design
- Trigger: Submitted
- Entry: Sample
- Exit: Quality review
- Inputs: Sample
- Outputs: Review
- Dependencies: IM-203
- Consulted: TTM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Quality sample.
- What next: IM-302

### IM-306 — Route approvals

- Category: Workflow & Approvals
- Stage: ST3 Coordinated Design
- Trigger: Items waiting
- Entry: Queue
- Exit: Routed
- Inputs: Queue
- Outputs: Routed
- Dependencies: IM-205
- Consulted: PDM, TTM
- Approver: PDM
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Move containers through approval states.
- What next: IM-307

### IM-307 — Manage information state changes

- Category: Workflow & Approvals
- Stage: ST3 Coordinated Design
- Trigger: Decision made
- Entry: State
- Exit: State changed
- Inputs: Decision
- Outputs: State
- Dependencies: IM-306
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: WIP / Shared / Published.
- What next: IM-401

### IM-308 — Manage escalations (information)

- Category: Workflow & Approvals
- Stage: ST3 Coordinated Design
- Trigger: Overdue
- Entry: Item
- Exit: Escalation
- Inputs: Item
- Outputs: Escalation
- Dependencies: None
- Consulted: PDM, DTL
- Approver: DTL
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Overdue or blocked containers.
- What next: DTL-301

### IM-401 — Publish information

- Category: Issue
- Stage: ST5 Issue
- Trigger: PDM-302
- Entry: Approved containers
- Exit: Published
- Inputs: Approvals
- Outputs: Published set
- Dependencies: PDM-302, DTL-501
- Consulted: PDM, DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: FS after PDM-302. No publish before PDM approval.
- What next: IM-402

### IM-402 — Update registers

- Category: Issue
- Stage: ST5 Issue
- Trigger: Published
- Entry: Registers
- Exit: Registers updated
- Inputs: Published
- Outputs: Registers
- Dependencies: IM-401
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: FS after publish.
- What next: IM-403

### IM-403 — Issue information containers

- Category: Issue
- Stage: ST5 Issue
- Trigger: Registers updated
- Entry: Issue list
- Exit: Containers issued
- Inputs: List
- Outputs: Issue event
- Dependencies: IM-402, DTL-502
- Consulted: PDM, DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Transmit / issue event.
- What next: IM-601

### IM-404 — Manage shared information

- Category: Information Exchange Management
- Stage: ST5 Issue
- Trigger: Ready to share
- Entry: Shared set
- Exit: Shared managed
- Inputs: Set
- Outputs: Shared
- Dependencies: IM-307
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Shared state control.
- What next: IM-401

### IM-601 — Manage revisions

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Revision approved
- Entry: Rev
- Exit: Revision issued
- Inputs: PDM-604
- Outputs: Revision issue
- Dependencies: PDM-604
- Consulted: PDM, DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Control revised packages on site.
- What next: IM-602

### IM-602 — Manage updated packages

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: Revision issued
- Entry: Package
- Exit: Status updated
- Inputs: Package
- Outputs: REVISED
- Dependencies: IM-601
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Keep package status REVISED.
- What next: IM-603

### IM-603 — Manage construction information exchanges

- Category: Construction Support
- Stage: ST6 Construction Support
- Trigger: On site
- Entry: Exchange
- Exit: Exchange recorded
- Inputs: Exchange
- Outputs: Record
- Dependencies: IM-403
- Consulted: CM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Exchanges during install.
- What next: IM-701

### IM-701 — Review AIM

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: S6 stable
- Entry: AIM
- Exit: AIM review
- Inputs: AIM engine
- Outputs: AIM review
- Dependencies: PDM-702
- Consulted: PDM, FM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Review AIM present vs required.
- What next: IM-702

### IM-702 — Review AIR compliance

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: AIM reviewed
- Entry: AIR
- Exit: AIR compliance
- Inputs: AIR
- Outputs: AIR compliance
- Dependencies: IM-701
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Before AIM approval / handover.
- What next: IM-703 / DTL-702

### IM-703 — Prepare handover and archive packages

- Category: Handover
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: AIR compliance
- Entry: Sets
- Exit: Handover + archive packs
- Inputs: Registers
- Outputs: Packs
- Dependencies: IM-702
- Consulted: DM, PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 3 / 0
- Why: Build handover + archive sets.
- What next: IM-704

### IM-704 — Archive information

- Category: Archive
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: DTL-708
- Entry: Archive pack
- Exit: Archived
- Inputs: Pack
- Outputs: Archive
- Dependencies: DTL-708
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Store the archive.
- What next: IM-705

### IM-705 — Lock information records

- Category: Archive
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Archived
- Entry: Records
- Exit: Locked
- Inputs: Archive
- Outputs: Lock
- Dependencies: IM-704
- Consulted: DM
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Prevent further mutation.
- What next: IM-706

### IM-706 — Generate final registers

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Locked
- Entry: Registers
- Exit: Final registers
- Inputs: Registers
- Outputs: Final registers
- Dependencies: IM-705
- Consulted: PDM
- Approver: —
- Mandatory: True
- Duration / lead (days): 2 / 0
- Why: Final MIDP/TIDP/issue registers.
- What next: IM-707

### IM-707 — Support lessons learned

- Category: Closeout
- Stage: ST7 Handover / Closeout / Archive / Operations transition
- Trigger: Final registers
- Entry: Evidence
- Exit: Evidence pack
- Inputs: Logs
- Outputs: Evidence
- Dependencies: IM-706
- Consulted: DTL
- Approver: —
- Mandatory: True
- Duration / lead (days): 1 / 0
- Why: Provide information evidence to DTL-705.
- What next: —
