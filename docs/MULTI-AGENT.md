# Atana Multi-Agent AI Platform v1.0

Implementation-ready design. Engines already exist. Agents orchestrate them.

```
User → Orchestrator → Specialist Agent → Atana engines → Graph / MIDP / AIR / AIM
                         ↓
                   HITL (class D–F)
                         ↓
                      Audit log
```

## Technology (target)

| Layer | Choice |
|---|---|
| Reasoning | Azure OpenAI + Azure AI Foundry |
| Skills / tools | Semantic Kernel (.NET 9) |
| Graph | Neo4j (PWA uses in-memory ATN_CHAIN today) |
| System of record | PostgreSQL |
| UI | This PWA now; React + Fluent later |
| Events | CloudEvents on the existing ecosystem bus |

## Orchestration

1. Classify intent (MIDP / AIR / compliance / exec / …).
2. Bind project + role + stage from session.
3. Load memory (last agent, last facts).
4. Call one specialist. Specialists may *ask* another agent; they may not silently mutate.
5. Class A–B: answer immediately.
6. Class C: propose plan.
7. Class D–F: require Approve on the Agents tab (human-in-the-loop).
8. Write audit: who, agent, class, mode (propose|execute|reject), object ids.

No agent is System of Record. SoR stays Atana engines + CDE.

## Agent specifications (14)

| Agent | Purpose | Sources | Graph | Default class | Escalate to |
|---|---|---|---|---|---|
| IM | Own OIR→AIM honesty | OIR PIR EIR AIR AIM MIDP | ATN_CHAIN | D | PDM / client IM |
| MIDP | Generate master plan | DPoW, packages, roles | Package CONTAINS | E | IM |
| TIDP | Team plans follow packages | tidpRows, LOIN | GENERATES | C | TTM |
| AIR | What is required for X | AIR ITE IDS ATA_ | REQUIRES | A | IM |
| AIM | Present vs required | AIM engine | Asset→AIM | A | FM |
| IDS | Spec validation | IDS engine | BINDS | B | TTIM |
| Compliance | Why is X low | TIDP + IDS + attrs | BLOCKS | A | IM |
| Asset | Ss = procured asset | packages | Package→Asset | A | FM |
| Workflow | WIP/Shared/Published | TIDP states | BLOCKS S4 | D | TTM |
| PM | What blocks the stage | MIDP TIDP DPoW | IMPACTS | A | PDM |
| Executive | One-sentence health | ECC scores | health | A | CEO / owner |
| FM | Operate readiness | AIM operate LOI | AIM→Ops | A | AM |
| Twin | Twin readiness only | AIM | planned | A | IM (parked telemetry) |
| Portfolio | Cross-project | all projects | portfolio | A | Exec |

### Prompt framework (every agent)

```
You are the {agent} for project {code} at work stage {stage}.
You may only use tools in your allow-list.
You may not change System of Record without class + HITL.
Answer with: finding, evidence (graph path or row ids), proposed action, class.
```

### Permissions

Map to existing seats: Owner / Custodian / Approver / Contributor / Reviewer / Consumer.  
Agent identity is a service principal; it inherits the invoking user's seat, never higher.

## Communication

- Orchestrator ↔ agent: JSON tool calls (`ask`, `propose`, `execute`).
- Agent ↔ agent: only via orchestrator (no peer mutation).
- Agent ↔ engine: existing functions (`generate`, `ensureTidpRowsForProject`, `atnAnswer`, `atnAimScore`).

## Memory

- Working: last 12 user facts on `project.atnAgentMemory`.
- Episodic: `project.atnAgentAudit`.
- Semantic: Knowledge Graph (production Neo4j).

## Security & audit

- No ACC/SharePoint write-back in this build (parking lot PL-16/17).
- Class E/F logged even when rejected.
- Prompts stored hashed + object ids, not raw secrets.

## APIs (target .NET)

```
POST /api/agents/route     { projectId, question }
POST /api/agents/{id}/ask
POST /api/agents/{id}/propose
POST /api/agents/{id}/execute   requires HITL token
GET  /api/agents/audit?projectId=
```

## Sequence (MIDP example)

User "Create a MIDP for a pump station"  
→ Orchestrator routes MIDP  
→ MIDP Agent reads teams + FBs + packages  
→ Proposes class E Generate  
→ Human Approve  
→ `generate()` + persist  
→ Audit execute  
→ IM Agent can then explain AIR gaps.

## Roadmap

| Phase | When | What |
|---|---|---|
| P0 | this build | 14 agents in PWA, router, HITL, audit |
| P1 | next | Semantic Kernel skills wrapping each engine |
| P2 | | Azure AI Foundry agents + Neo4j tool |
| P3 | | Portfolio + Twin agents live (not parked) |
| P4 | | Multi-project lakehouse (separate prompt) |

## Parking lot

PL-01…PL-23 unchanged. Agents must not pretend catalogues or ACC write-back exist.
