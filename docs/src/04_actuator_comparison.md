# Preliminary actuator architecture comparison

Values marked (S..) come from the source manifest. Values marked ~ are typical catalogue-class figures that were **not verified in this session** and must be checked against the chosen part's datasheet before ordering.

| Criterion | **A. Industrial compact ball-screw stages** (THK KR20/KR26, MISUMI LX20/LX26, Oriental DRS2 for Z) | **B. Low-cost integrated stages** (FUYU FSL30/FSK30, generic MGN12 + SFU08/12 ball screw + NEMA17) | **C. Custom** (MGN12H rail + Tr8×2 single-start lead screw + NEMA17) |
|---|---|---|---|
| Travel availability | KR20: 30–130 mm (S30), so Z {{WB_TRAVEL_Z}} mm and X {{WB_TRAVEL_X}} mm (W-B) fit; W-A's X {{WA_TRAVEL_X}} mm needs KR26/LX26; LX26: lead 2/5 mm (S31) | 50–300 mm (S33) | any |
| Repeatability | ~±0.003 mm (precision grade) to ~±0.01 mm; DRS2 ±0.003 (ground) / ±0.01 (rolled) (S32) | position accuracy 0.05 mm quoted (S33); repeatability ~±0.01–0.02, batch dependent | ~±0.01–0.02 mm with single-direction approach; depends on assembly |
| Backlash | ~≤0.02 mm, preloaded nut options | ~0.01–0.03 mm | 0.05–0.1 mm with a plain brass nut; ~0.01–0.02 with an anti-backlash POM nut (wears) |
| Lead / resolution | 1 or 2 mm, so 5–10 µm per full step | 1–5 mm typical | 2 mm, so 10 µm per full step |
| Rigidity | high: U-rail with integrated guide (S30) | medium: extruded body, small blocks | medium: depends on the base plate you design |
| Size (width class) | 20–26 mm | 30–40 mm | 27 mm carriage, plus screw offset |
| Moving mass | low–medium | medium | low |
| Assembly effort | bolt-on; motor bracket supplied | bolt-on | high: alignment of screw, rail and bearings |
| Availability (Japan) | good via MISUMI/THK/Oriental distributors | online marketplaces; lead time and QC vary | all parts common |
| Serviceability | documented, grease ports, spares | limited documentation | fully user-serviceable |
| Suitability around IX73 | best: compact bodies keep the X cantilever light and the Z envelope narrow | acceptable for Y (fixed beam); weaker as a cantilevered X | acceptable for Y; weakest for Z (backlash) |
| Typical cost (rough) | highest (~JPY 50–120k per axis) | lowest | lowest in parts, highest in labour |

## Recommendation (to be frozen only after the geometry is validated)

- **Z: architecture A, 1 mm lead ball screw** (THK KR20 class, stroke ≥ {{WB_TRAVEL_Z}} mm; the next catalogue stroke up), or an Oriental DRS2 guide type with brake if a closed-loop absolute axis is preferred. Z sets landing accuracy and must not drop, so this is where the money should go.
- **X: architecture A** (KR20/LX26 class, stroke ≥ {{WB_TRAVEL_X}} mm in W-B or {{WA_TRAVEL_X}} mm in W-A, lead 1–2 mm). It is the cantilevered axis, so body stiffness and low mass matter most.
- **Y: A or B.** It is fixed on a supported beam, so a good integrated stage from B is acceptable. Choose A if one supplier and consistent documentation matter.
- **Architecture C** is kept as a comparison and fallback. It is appropriate only if lead times block A/B. In that case, use a Tr8×2 single-start screw (2 mm lead, **not** Tr8×8), an anti-backlash nut, a fixed-floating bearing arrangement, and always approach from one direction.

This mix fits the stated budget order (about JPY 200k, cost secondary) with A on X and Z. The exact part numbers are **not** frozen (see `07_…`).
