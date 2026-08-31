# Atana Knowledge Graph Engine

Operational graph lives **inside** `Atana-IM-Tasks.html` (version 3.6.1),
tabs **Graph** and **Decide**. No Neo4j process in this file.

Production target remains Neo4j + GraphQL + .NET 9 + Azure OpenAI
(see architecture docs in the repo root).

## Information chain

Client requirement → OIR → PIR → EIR → AIR → Information Template →
Information Requirement → Scope Production Package → Deliverable → IDS →
AIM → Asset → Digital Twin → Operations.

FB01 seed reverse walk (Graph → Trace):

Fire Rating → Door template → AIR → EIR → PIR → OIR

Forward walk (Graph → Impact) is a BFS along `IMPACTS` / `BLOCKS` /
`FEEDS` / `PRODUCES` / `CONTAINS`.

## Node kinds (`ATN_KINDS`)

Organisation, Project, Portfolio, Functional Breakdown, Spatial Breakdown,
Task Team, Stakeholder, Role, Work Stage, Scope Production Package,
Information Template, Information Requirement, Attribute, Parameter,
Deliverable, Deliverable Package, Information Container, IDS, AIM, AIR,
EIR, PIR, OIR, Asset, Asset Type, System, System Type, Space, Space Type,
Workflow, Approval, Action, Recommendation, Prediction, Issue, Risk,
Compliance Result, Validation Result, Requirement, Classification,
Uniclass SS, Uniclass SL, IFC Property Set, Revit Parameter, Document,
Model, Drawing, Report, Specification, Schedule, Calculation, Register,
Matrix, Digital Twin Entity, Operations Entity, Facility,
Maintenance Activity, Lifecycle Stage.

## Relationship kinds (`ATN_REL_KINDS`)

REQUIRES, GENERATES, DEPENDS_ON, OWNS, BELONGS_TO, SATISFIES, VALIDATED_BY,
APPROVED_BY, AUTHORED_BY, MANAGED_BY, CLASSIFIED_AS, LOCATED_IN, PART_OF,
TRACES_TO, DERIVED_FROM, RELATED_TO, SUPPORTS, FEEDS, REFERENCES, CONTAINS,
BLOCKS, ENABLES, IMPACTS, ASSIGNED_TO, RESPONSIBLE_FOR, INFORMS, MONITORS,
GOVERNS, BINDS, DEFINES, PRODUCES.

## Named queries (`ATN_QUERIES`)

- What information is missing?
- Which assets are non-compliant?
- Which deliverables support this requirement?
- Why is Fire Rating required?
- What is blocking Stage 4?
- Which stakeholders are impacted?
- Which assets will fail handover?
- Which client requirements are not satisfied?
- Which systems have the highest risk?
- Which deliverables are ready for issue?
- What information must be delivered next?
- What is the current project health?
- Which AHUs are missing mandatory AIR information?
- Generate a recovery plan for Stage 4.
- Show traceability from OIR to Asset.
- Why is HVAC compliance below target?

Answers are produced by `atnAnswer` / `atnWhy` / `atnImpact` from the
in-memory seed graph plus project AIM present-vs-required scores
(`atnAimScore`). Completeness = present ÷ required. Stage 4 gate uses
the 95% AIM threshold.

## Persona dashboards (`ATN_DASHBOARDS`)

Executive, Client, Asset Owner, Project Manager, Project Delivery Manager,
Information Manager, Task Team Manager, Information Author, Facility Manager,
Operations Manager.

## Persistence

`localStorage` key `atana_im_engines_v1` stores present attributes,
selected persona, AIR LOI, and selected asset types.

## Security / multi-tenant (production note)

This HTML is a single-user operational graph. Tenant isolation, RBAC,
and audit belong in the Neo4j / GraphQL / .NET target — not in this file.

## Roadmap (parked)

- ACC / SharePoint CDE write-back
- Live digital twin bindings
- Multi-agent AI platform
- Executive command center
- Neo4j runtime + GraphQL schema
