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

## Decision (frozen as the V1 baseline in issue #12)

"Tip travel" is what the capillary tip must cover; "actuator stroke" is the catalogue stroke bought, which is at least the tip travel (`03_architecture.md` §3).

All three axes are architecture A (MISUMI LX family, S39), with three Oriental PKP244D15A2 motors (S42) and one ADI/Trinamic TMCM-3110-TMCL controller driven from Python (`06_electrical.md`).

- **Z: MISUMI LX20 precision grade, lead 1 mm, motor direct-coupled** (tip travel {{WB_TRAVEL_Z}} mm, catalogue actuator stroke {{WB_STROKE_Z:.0f}} mm in the model). Landing height is the most sensitive axis, so Z keeps the direct coupling: no belt stage and the least backlash. It must not drop unpowered (`03_architecture.md` §5).
- **X: MISUMI LXR26, lead 2 mm, motor folded back** (tip travel {{WB_TRAVEL_X}} mm → actuator stroke {{WB_STROKE_X:.0f}} mm). The timing belt sits only between the motor and the ball screw; positioning is still by the ball screw. Folding the motor beside the actuator shortens the envelope: the tower now sits {{WB_TOWER_X}} mm from the optical axis in the model (368 mm with direct-coupled motors). X/Y repeatability matters more than absolute accuracy, because the image calibration absorbs systematic offsets.
- **Y: MISUMI LXR26, lead 2 mm, motor folded back** (tip travel {{WB_TRAVEL_Y}} mm → actuator stroke {{WB_STROKE_Y:.0f}} mm). Its carriage carries the X and Z groups (≈{{MASS_Y:.1f}} kg, largest moment ≈{{MOM_Y:.1f}} N·m, `03_architecture.md` §5b). **Open check:** the LXR26 allowable static moments (MP/MY/MR) were not readable here and must be compared with this value before ordering.
- The SpheroidPicker (S20) drove M8 threaded rods (2 mm pitch) directly with NEMA17 motors and mechanical end stops; ball-screw LX/LXR stages should repeat substantially better while keeping the same vision-guided correction.
- **Architecture C** is kept as a comparison and fallback. It is appropriate only if lead times block A/B. In that case, use a Tr8×2 single-start screw (2 mm lead, **not** Tr8×8), an anti-backlash nut, a fixed-floating bearing arrangement, and always approach from one direction.

The configured MISUMI part numbers, the LXR26 allowable moments and the PKP244D15A2 current setting are the remaining open checks in issue #12 (see also `07_…`).
