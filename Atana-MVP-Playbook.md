# Atana MVP Playbook — FB01 Administration Building

Scope of this pilot: Phases 1–5 only.

FB01 Administration Building
- Wall systems Ss_25_10_20
- Door systems Ss_25_30_20
- Window systems Ss_25_30_95
- Floor systems Ss_30_20_00
- Ceiling systems Ss_30_25_00

One Production Package per FB + Ss. Workstage is maturity.

TIDP on each package:
Model (IA) → Coordinate (TTIM) → Verify (TTIM) → Review (PR) → Approve (TTM)

PPDM:
- Windows depend on Walls (D01 Geometric, LOD2/LOI2)
- Doors depend on Walls (D01 Geometric, LOD2/LOI2)
- Ceilings depend on Walls (D02 Spatial) and Floors (D02 Spatial)

Not in this pilot: interfaces, model packages, MVF, information packages, knowledge graph, Copilot, AI.

Test:
1. IM Planner → MVP → Load FB01 pilot
2. Open Window systems — Walls must appear as a dependency
3. Each package has five TIDP rows with FRRM roles
4. Change current workstage — package IDs stay the same
