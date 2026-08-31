# Atana Operating Model & Governance Framework v1.0

**Status:** Implementation-ready  
**Date:** 2026-08-31  
**Companion:** `Atana-Operating-Model-v1.0.docx`, `Atana-Governance-RACI-v1.0.xlsx`, `Atana-Governance-Objects-v1.json`

This document does **not** redesign DPoW, packages, templates, OIR/PIR/EIR/AIR/AIM, IDS, MIDP/TIDP, Decision Intelligence or the Knowledge Graph. Those engines already exist.

It answers the question the engines cannot:

> Who is allowed to change the operating system, and by what procedure?

Without this, Atana is a toolkit. With it, Atana is operable as an Information Lifecycle Operating System.

---

## 1. Principles

1. **Separate duty from tool access.** A role in Entra or the PWA is not ownership. Ownership is declared on the object.
2. **One Owner per object version.** Shared ownership is an escalation path, not a default.
3. **Custodian ≠ Owner.** The Information Manager often custodians what the appointing party owns.
4. **Catalogue changes are organisation events.** Project teams consume catalogues; they do not fork Uniclass or door templates quietly.
5. **AI may recommend. A named human accepts.** Recommendations are SoI. Acceptance writes SoR.
6. **Audit is mandatory on every state change.** who, when, why, oldValue, newValue — already in `Atana-Governance-Framework.json`.
7. **Precedence is unchanged:** USER > ASSET > PROJECT > ORGANISATION > SYSTEM. Governance decides *who may use* each layer, not a sixth layer.
8. **Admin tiers are unchanged:** SYSADMIN → ORGADMIN → PROJECTADMIN → TTM. TTM cannot edit global rules.

ISO 19650 parties map onto Atana roles; they are not replaced.

| ISO 19650 party | Typical Atana seat |
|---|---|
| Appointing party | Client / Asset Owner / ORGADMIN sponsor |
| Lead appointed party | PDM + IM (delivery + information) |
| Appointed party / task team | TTM, TTIM, IA, PR, DTL |
| Asset operator | FM / Ops / Twin steward after handover |

---

## 2. Operating structure

Three standing planes, one project plane.

```
Organisation Governance Board
        │
        ├── Portfolio Information Office
        │         └── Project Information Function
        │
        ├── Catalogue & Classification Office
        ├── Template Office
        ├── AI & Graph Office
        └── Twin & Operations Office
```

| Plane | Mandate | Cadence | Chair |
|---|---|---|---|
| Organisation Governance Board (OGB) | Policy, catalogues, AI policy, twin policy, exceptions | Monthly + emergency | ORGADMIN / CDO equivalent |
| Portfolio Information Office (PIO) | Cross-project standards, reuse, lessons | Fortnightly | Portfolio IM |
| Project Information Function (PIF) | This project's AIR/AIM/MIDP/gates | Weekly + gates | Project IM |
| Catalogue Office | Uniclass, asset/system/space libraries | Change window monthly | Classification steward |
| Template Office | Information templates, shared parameters | Change window monthly | Template steward |
| AI & Graph Office | Prompts, allowed tools, graph schema extensions | Monthly | AI governance officer + Graph steward |
| Twin & Operations Office | Handover accept, twin DTDL, opsWins policy | Per handover + quarterly | Twin steward + FM |

A small organisation collapses offices onto two people. The **duties** remain; the **hats** stack. A large owner-operator splits them.

### 2.1 Admin tiers (already specified — applied)

| Tier | May | May not |
|---|---|---|
| SYSADMIN | Platform features, tenants, encryption, connector runtimes | Tenant catalogues without ORGADMIN |
| ORGADMIN | Org policy, catalogues, template library, AI policy, role catalogue | Another tenant |
| PROJECTADMIN | Project bindings, project overrides, team membership, gate thresholds within policy band | Global rules, Uniclass master, org templates |
| TTM | Team TIDP, assignments, package locks within team | Global rules, other teams' AIR, catalogues |

---

## 3. Role catalogue

Existing delivery roles stay. Governance adds a small number of **steward** roles. Stewards are duties; they may be held by people who already hold IM / ORGADMIN.

### 3.1 Delivery roles (project)

| Code | Role | Primary duty |
|---|---|---|
| AP | Appointing party sponsor | Owns OIR; accepts PIR/EIR |
| AO | Asset owner | Owns AIR intent and AIM accept at handover |
| PDM | Project delivery manager | Time, cost, package commercial tags, stage decision with IM |
| IM | Information Manager | Custodian of the project information operating system |
| DM | Document / CDE manager | Container state in the CDE (file SoR) |
| DTL | Discipline lead | Technical fitness of a discipline package |
| TTM | Task team manager | Team output and TIDP |
| TTIM | Task team information manager | Team IR/IDS hygiene |
| IA | Information author | Creates containers and parameter values |
| PR | Peer reviewer | Reviews before Shared |
| FM | Facility manager | Consumes AIM; owns ops observations after handover |
| OPS | Operations manager | Owns live regime; not AIR |

### 3.2 Steward roles (organisation / portfolio)

| Code | Role | Primary duty |
|---|---|---|
| OGB | Governance board member | Policy decisions |
| PIM | Portfolio information manager | Reuse, benchmarking readiness |
| CS | Classification steward | Uniclass and mapping tables |
| TS | Template steward | Information templates + ATA_ZZ |
| GS | Graph steward | Node/rel kinds, query catalogue |
| AIG | AI governance officer | Allowed models, tool scopes, accept rules |
| TWS | Twin steward | DTDL versions, identity to AIM |
| AS | Asset library steward | Asset types |
| SS | System library steward | System types |
| SP | Space library steward | Space types |

One person may hold IM + TS on a small programme. They still record both duties on the object.

---

## 4. Duty model (every governed object)

Six seats. Empty seats are explicit (`unassigned` is a defect, not a default to IM).

| Seat | Meaning | Typical count |
|---|---|---|
| **Owner** | Accountable for fitness for purpose. Loses sleep. | 1 |
| **Custodian** | Versioning, access, integrity, audit completeness | 1 |
| **Approver** | May move DRAFT → ACTIVE / lock a stage issue | 1 (or named board) |
| **Contributor** | May create a draft or proposed change | many |
| **Reviewer** | Must review before approve | named set |
| **Consumer** | May read and use; may not edit | many |

RACI mapping used in the matrix workbook:

| Seat | RACI |
|---|---|
| Owner | A |
| Custodian | R (maintain) |
| Approver | A (state change) — same person as Owner unless policy splits |
| Contributor | R (draft) |
| Reviewer | C |
| Consumer | I |

FRRM (already in the platform) stays for *deliverable workflow*:

| Code | Meaning on a container |
|---|---|
| O | Originate |
| A | Approve (task team) |
| V | Verify (TTIM / IM) |
| R | Review (peer) |
| P | Publish (IM / PDM) |

FRRM does not replace object ownership. An IA can Originate a door schedule without owning the Door template.

---

## 5. Object governance

Default seats. Projects may *narrow* consumers; they may not reassign Owner of an organisation catalogue object.

### 5.1 OIR

| Seat | Default |
|---|---|
| Owner | Appointing party sponsor (AP) |
| Custodian | Portfolio IM or project IM if single-project owner |
| Approver | AP (board if regulated asset) |
| Contributor | IM, PIM, client SMEs |
| Reviewer | AO, legal / H&S as named |
| Consumer | All appointed parties |

**Change procedure:** draft in Atana → OGB or AP approval → version bump → projects inherit on next stage, not mid-gate unless exception.

### 5.2 PIR

| Seat | Default |
|---|---|
| Owner | AP (project-specific expression of OIR) |
| Custodian | IM |
| Approver | AP + PDM noted |
| Contributor | IM, PDM |
| Reviewer | AO, DTL as relevant |
| Consumer | Task teams |

PIR cannot weaken an OIR. Conflicts escalate to OGB.

### 5.3 EIR

| Seat | Default |
|---|---|
| Owner | AP (appointment document) |
| Custodian | IM |
| Approver | AP |
| Contributor | IM, PDM, DTL |
| Reviewer | Lead appointed party legal/commercial |
| Consumer | All appointed parties |

EIR is the appointment-facing contract of information. Changing it after award is a **contract variation**, not a catalogue edit.

### 5.4 AIR

| Seat | Default |
|---|---|
| Owner | Asset owner |
| Custodian | IM (project) then FM/TWS after handover |
| Approver | AO |
| Contributor | IM, TS, DTL, TTIM |
| Reviewer | FM, CS (classification impact) |
| Consumer | Authors, twin, CMMS adapters |

**Who can create AIR?** Contributor list above. **Who can activate it?** Approver = AO. Project teams propose; they do not activate organisation-standard AIR types.

### 5.5 AIM

| Seat | Default |
|---|---|
| Owner | Asset owner |
| Custodian | IM until `aim.accepted`; then FM |
| Approver | AO at handover; IM at interim snapshots |
| Contributor | IA, TTIM (observations) |
| Reviewer | IM, FM |
| Consumer | Twin, CMMS, exec dashboards |

Completeness formula is not negotiable at project level (`present/required` at named LOI). Gate **threshold** may move inside the org policy band (default Stage 4 = 95%).

### 5.6 IDS

| Seat | Default |
|---|---|
| Owner | Template steward (spec) / IM (project run) |
| Custodian | IM |
| Approver | TS for spec; IM for declaring a run authoritative |
| Contributor | TTIM, IA (fix model), TS (spec) |
| Reviewer | DTL |
| Consumer | Graph, Decide, CDE adapters |

An IDS fail is an observation. Declaring it a **gate input** is an IM act.

### 5.7 Scope production packages

| Seat | Default |
|---|---|
| Owner | TTM of the responsible team |
| Custodian | TTIM |
| Approver | TTM (team) + IM (if package locked at project) |
| Contributor | DTL, IA |
| Reviewer | IM, PDM |
| Consumer | Authors, PDM, Decide |

Locked packages cannot be USER_REMOVED (already specified). Unlock = IM + TTM.

### 5.8 Information templates

| Seat | Default |
|---|---|
| Owner | Template steward |
| Custodian | Template steward |
| Approver | OGB or delegated TS |
| Contributor | IM, DTL, CS |
| Reviewer | CS, AO (if AIR-facing) |
| Consumer | All projects |

Project-level template clone is an **override** (USER/PROJECT layer), expires at project close unless promoted.

### 5.9 Information requirements

| Seat | Default |
|---|---|
| Owner | Owner of the parent (AIR or EIR) |
| Custodian | IM |
| Approver | Same as parent |
| Contributor | TTIM, TS |
| Reviewer | DTL |
| Consumer | IA, IDS |

### 5.10 Deliverables (plan row vs file)

| Seat | Plan row | File / container |
|---|---|---|
| Owner | TTM | CDE SoR remains the CDE |
| Custodian | TTIM | DM |
| Approver | TTM then IM/PDM at Publish | CDE workflow + Atana P |
| Contributor | IA | IA |
| Reviewer | PR, TTIM | PR |
| Consumer | Project | Project + archive |

Atana owns the *plan*. The CDE owns the *bytes*. Governance must not pretend otherwise (see Ecosystem Architecture).

### 5.11 Workflows

| Seat | Default |
|---|---|
| Owner | ORGADMIN (org workflow catalogue) |
| Custodian | IM on the project instance |
| Approver | OGB for catalogue; IM for project deviation within band |
| Contributor | PROJECTADMIN |
| Reviewer | PDM, DM |
| Consumer | All delivery roles |

TTM cannot invent a sixth state that skips Verify.

### 5.12 Knowledge graph

| Seat | Default |
|---|---|
| Owner | Graph steward (schema) / IM (project graph data) |
| Custodian | GS / IM |
| Approver | GS for new node/rel kinds; IM for project edges that are not seed |
| Contributor | Engines (automatic), IM |
| Reviewer | AIG if an agent wrote an edge |
| Consumer | Decide, Copilot, dashboards |

Schema extensions are organisation events. Project data is project event.

### 5.13 AI recommendations

| Seat | Default |
|---|---|
| Owner | AIG (policy) / PDM or IM (accepted action, by type) |
| Custodian | IM |
| Approver | Named human by recommendation class (see §8) |
| Contributor | Agents, Decide |
| Reviewer | IM always; AO if AIM-affecting |
| Consumer | Assigned role |

**No agent may write AIR, catalogues, gate thresholds, or AIM accept.**

### 5.14 Asset / system / space libraries

| Seat | Asset | System | Space |
|---|---|---|---|
| Owner | AS | SS | SP |
| Custodian | same | same | same |
| Approver | OGB or delegated steward | same | same |
| Contributor | IM, DTL | IM, DTL | IM |
| Reviewer | CS | CS | CS |
| Consumer | All projects |

### 5.15 Classification library

| Seat | Default |
|---|---|
| Owner | Classification steward |
| Custodian | CS |
| Approver | OGB |
| Contributor | TS, AS, SS, SP |
| Reviewer | IM community (named) |
| Consumer | All engines |

Uniclass mappings are not project opinions. A project may *propose* a map; CS activates it.

---

## 6. Governance by plane

### 6.1 Organisation

Owns: policy, role catalogue, default gates, AI policy, connector policy, catalogue masters, encryption / residency.

Decisions: new steward appointment; retiring a template; allowing `naming.enforce`; allowing `opsWinsAfterHandover`; adding a node kind.

### 6.2 Portfolio

Owns: reuse of AIR types across projects; lessons promotion; benchmark definitions (used later by Portfolio Intelligence).

Decisions: promote a project override into org catalogue; waive a gate across a programme (exception record required).

### 6.3 Project

Owns: bindings, team membership, project PIR/EIR instance, MIDP run, gate instance within band, conflict accept.

Decisions: issue Stage 4; accept interim AIM snapshot; raise variation to EIR (then AP).

### 6.4 Information

Owns: present vs required honesty. IM can stop a gate. PDM cannot override a fail without an exception signed by AP/AO.

### 6.5 Classification / templates / workflow

Change windows. Emergency patch = OGB chair + steward, ratified at next board.

### 6.6 AI

See §8.

### 6.7 Knowledge graph

Schema under GS. Seed walks (Fire Rating) are fixtures; projects do not delete platform seed kinds.

### 6.8 Digital twin

Twin identity = `atana.assetId`. DTDL version locked to template version. Telemetry never overwrites nameplate AIM. Handover accept is AO + IM + FM.

---

## 7. Decision rights matrix (summary)

| Decision | Rights holder | Must consult | Escalate if |
|---|---|---|---|
| Publish org template | TS + OGB | CS, IM community | AIR impact unknown |
| Activate AIR type | AO | IM, FM, TS | Conflicts with EIR |
| Change Stage 4 threshold | ORGADMIN within 90–98%; below 90% = OGB | IM, PDM | Programme-wide waive |
| Lock / unlock package | IM + TTM | PDM | Commercial impact |
| Accept AIM handover | AO | IM, FM, TWS | Completeness < gate |
| Accept AI action (P1) | IM or PDM per class | Affected TTM | AIM/AIR write requested |
| Add graph node kind | GS + OGB | AIG | Breaks `/v1/ask` |
| Bind primary CDE | PROJECTADMIN | IM, DM | Second file SoR requested |
| Promote lessons to catalogue | PIM + steward | OGB | Changes AIR |
| Exception to skip Verify | Forbidden | — | — |

---

## 8. AI governance

Classes of recommendation (Decide / future agents):

| Class | Example | Approver | Auto-apply? |
|---|---|---|---|
| A Inform | “HVAC compliance is 71%” | none (SoI) | n/a |
| B Assign | “Give D-02 Fire Rating to IA-03” | IM | No |
| C Plan | “Generate MIDP for S4 extras” | IM + PDM | No |
| D Gate | “Block Stage 4” | IM (system may raise; human confirms notify) | Raise yes, waive no |
| E Mutate | “Add Fire Rating to template” | TS + OGB | Never |
| F Handover | “Accept AIM for D-02” | AO | Never |

Logging: prompt/tool versions, graph citations, accept/reject, who.

Human-in-the-loop is not optional for C–F.

---

## 9. Escalation

| Level | Time | Path |
|---|---|---|
| L1 | 1 working day | TTIM → IM |
| L2 | 3 working days | IM → PDM |
| L3 | 5 working days | PDM → AP / PROJECTADMIN |
| L4 | next OGB / 10 days | AP → OGB |
| L5 | emergency | OGB chair + SYSADMIN if platform |

ConflictRecords from the ecosystem fabric enter at L1 if mapping; L3 if they block a gate.

---

## 10. Operating procedures (minimum set)

| ID | Procedure | Owner | Trigger |
|---|---|---|---|
| SOP-01 | Stand up a project in Atana | IM | Appointment |
| SOP-02 | Bind primary CDE | PROJECTADMIN | After SOP-01 |
| SOP-03 | Generate MIDP | IM | Stage start |
| SOP-04 | Issue information gate | IM + PDM | Stage end |
| SOP-05 | Raise catalogue change | Steward | RFC |
| SOP-06 | Approve catalogue change | OGB | Monthly window |
| SOP-07 | Resolve ConflictRecord | IM | Event |
| SOP-08 | Accept / reject AI action | Named approver | Decision raised |
| SOP-09 | AIM handover accept | AO + IM + FM | S6 / contract |
| SOP-10 | Incident — wrong AIR live | IM + TS | Defect |
| SOP-11 | Access review | ORGADMIN | Quarterly |
| SOP-12 | Audit pack export | IM | Client / ISO audit |

### 10.1 Versioning procedure

- Catalogues: `MAJOR.MINOR` + `DRAFT | ACTIVE | RETIRED` (already specified).
- ACTIVE objects are immutable. Edit = new version.
- Projects pin `catalogueVersion` at each gate. Mid-gate hot-patch requires exception.
- AIM snapshots are immutable (`aimSnapshotId`).
- Graph schema versions independently of project data.

### 10.2 Audit procedure

Every state change writes the existing change tuple. Quarterly ORGADMIN reviews: orphan objects (`unassigned` owner), AI actions applied without accept, dual file SoR bindings, gate waivers. Export to SIEM as designed in the ecosystem spec.

---

## 11. Approval hierarchies

```
SYSADMIN
   └── ORGADMIN / OGB
          ├── Stewards (CS TS GS AIG TWS AS SS SP)
          ├── Portfolio IM
          └── PROJECTADMIN
                 ├── PDM
                 ├── IM
                 │     ├── DM
                 │     └── TTIM
                 └── TTM
                       ├── DTL
                       ├── PR
                       └── IA
```

Appointing party and asset owner sit **beside** this tree, not under TTM. They approve OIR/EIR/AIR/AIM even when they are not in the delivery org chart.

---

## 12. Implementation roadmap

Do not code this into the HTML console as a new product. Wire duties onto objects first.

| Wave | What | Exit |
|---|---|---|
| G0 | This framework + RACI workbook adopted | OGB named, even if two people |
| G1 | Object records carry Owner / Custodian / Approver | No ACTIVE catalogue with `unassigned` |
| G2 | SOP-01..04 used on one live project | Stage gate pack includes RACI extract |
| G3 | Catalogue RFC + version pin at gates | Project cannot edit org Door template |
| G4 | AI accept log on Decide actions | Class E/F blocked in API |
| G5 | Handover accept workflow with AO/FM | AIM snapshot immutable |

Parked product work (multi-agent, command center, twin platform, portfolio intelligence) **consumes** this model. They do not invent parallel roles.

---

## 13. What this is not

- Not a new engine.
- Not a replacement of ISO 19650 appointment documents.
- Not last-write-wins administration.
- Not “the IM owns everything.” The IM custodians much; the appointing party and asset owner still own purpose.
