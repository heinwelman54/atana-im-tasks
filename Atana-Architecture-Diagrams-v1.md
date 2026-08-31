# Atana Architecture Diagrams v1.0
Paste blocks into mermaid.live or any Mermaid renderer.

## 1. Logical ERD

```mermaid
erDiagram
  ORGANISATION ||--o{ PROJECT : owns
  ORGANISATION ||--o{ USER : employs
  ORGANISATION ||--o{ TASK_TEAM : catalogues
  PROJECT ||--o{ FUNCTIONAL_BREAKDOWN : has
  PROJECT ||--o{ SPATIAL_BREAKDOWN : has
  PROJECT ||--o{ DELIVERY_STAGE : has
  PROJECT ||--o{ PRODUCTION_PACKAGE : scopes
  PROJECT ||--o{ GENERATION_RUN : runs
  PROJECT ||--o{ DELIVERABLE : registers
  USER ||--o{ USER_ASSIGNMENT : assigned
  PROJECT ||--o{ USER_ASSIGNMENT : staffs
  TASK_TEAM ||--o{ USER_ASSIGNMENT : hosts
  FUNCTIONAL_ROLE ||--o{ USER_ASSIGNMENT : grants
  FUNCTIONAL_BREAKDOWN ||--o{ PRODUCTION_PACKAGE : contains
  SYSTEM ||--o{ PRODUCTION_PACKAGE : classifies
  SYSTEM ||--o{ ASSET : groups
  RULE ||--o{ GENERATION_RUN : pinned
  GENERATION_RUN ||--o{ DELIVERABLE : emits
  INFORMATION_CONTAINER ||--o{ DELIVERABLE : stores
  DELIVERABLE ||--o{ WORKFLOW_TRANSITION : traces
  RULE ||--o{ RULE_DEPENDENCY : expands
  PROJECT ||--o{ OVERRIDE : specialises
  CATALOGUE_VERSION ||--o{ RULE : versions
  CATALOGUE_VERSION ||--o{ GENERATION_RUN : pins
```

## 2. Rule execution

```mermaid
flowchart TD
  A[Project setup] --> B[Load teams and generation models]
  B --> C[Evaluate triggers]
  C --> D{SYSTEM / ASSET / SPACE / OPTIONAL / STAGE}
  D -->|fired| E[Build package list]
  D -->|not fired| X[Skip]
  E --> F[Expand dependencies]
  F --> G[Flatten by stage gate]
  G --> H[Apply precedence USER to SYSTEM]
  H --> I[Drop USER_REMOVED and honour locks]
  I --> J[Assign container and form]
  J --> K[Number per originator FB spatial form role]
  K --> L[Stamp IR and workflow roles]
  L --> M[Persist generated MIDP]
  M --> N[TIDP = filter by task team]
```

## 3. Generation workflow

```mermaid
flowchart LR
  P[Project] --> S[Spatial]
  P --> F[Functional]
  P --> T[Task teams]
  P --> Y[Systems]
  P --> A[Assets]
  P --> C[Spaces]
  P --> G[Stages]
  S --> R[Rule engine]
  F --> R
  T --> R
  Y --> R
  A --> R
  C --> R
  G --> R
  R --> K[Packages]
  K --> D[Deliverable containers]
  D --> M[MIDP]
  M --> I[TIDP per team]
  D --> W[WIP to Published]
```

## 4. ISO 19650 states

```mermaid
stateDiagram-v2
  [*] --> WIP: IA create
  WIP --> PEER_REVIEW: submit
  PEER_REVIEW --> WIP: reject
  PEER_REVIEW --> SHARED: approved for sharing
  SHARED --> TTM_APPROVAL: TTIM verified
  TTM_APPROVAL --> PUBLISHED: TTM plus IM PDM
  PUBLISHED --> ARCHIVED: close-out
```

## 5. Copilot read path

```mermaid
flowchart TD
  Q[Question] --> API[Atana API]
  API --> PP[Production package]
  PP --> DEP[Dependencies]
  PP --> IR[Information requirements]
  PP --> DEL[Deliverables]
  DEL --> IP[Information package]
  DEP --> ANS[Cited answer]
  IR --> ANS
  IP --> ANS
```

## 6. Information Requirements Engine

```mermaid
erDiagram
  IR_CATALOGUE ||--o{ INFORMATION_REQUIREMENT : contains
  SCOPE_PRODUCTION_PACKAGE ||--o{ SPP_STAGE_TARGET : matures
  SCOPE_PRODUCTION_PACKAGE ||--o{ SPP_IR_LINK : requires
  INFORMATION_REQUIREMENT ||--o{ SPP_IR_LINK : applied
  SCOPE_PRODUCTION_PACKAGE ||--o{ SPP_DELIVERABLE_LINK : evidenced
  DELIVERABLE ||--o{ SPP_DELIVERABLE_LINK : supports
  SCOPE_PRODUCTION_PACKAGE ||--o{ IR_OBSERVATION : measured
  INFORMATION_REQUIREMENT ||--o{ IR_OBSERVATION : observed
```

```mermaid
flowchart TD
  WB[LOI workbook] --> CAT[IR catalogue]
  CAT --> IR[InformationRequirement]
  TT[Task team] --> SPP[Scope production package]
  SS[Uniclass Ss] --> SPP
  SPP --> ST[Stage LOD LOI]
  IR --> LINK[spp_ir_links]
  SPP --> LINK
  LINK --> COMP[Compliance percent]
  OBS[Model or CDE observation] --> COMP
  SPP --> DEL[Required deliverables]
  COMP --> GATE[Workstage information gate]
```

## 7. AIM Engine

```mermaid
erDiagram
  ASSET_TYPE ||--o{ AIM_ASSET : instantiates
  ASSET_TYPE ||--o{ ASSET_TYPE_IR : requires
  INFORMATION_REQUIREMENT ||--o{ ASSET_TYPE_IR : defines
  ASSET_TYPE ||--o{ ASSET_TYPE_DELIVERABLE : needs
  SCOPE_PRODUCTION_PACKAGE ||--o{ AIM_ASSET : contains
  AIM_ASSET ||--o{ IR_OBSERVATION : measured_via_spp
```

```mermaid
flowchart TD
  SPP[Scope production package] --> AT[Asset type]
  AT --> IR[Required IR]
  AT --> DEL[Required deliverables]
  AT --> INST[Asset instance]
  INST --> OBS[Observations]
  IR --> COMP[Completeness percent]
  OBS --> COMP
  COMP --> DASH[Doors 85 percent]
  COMP --> AIR[AIR later]
```
