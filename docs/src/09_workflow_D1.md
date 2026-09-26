# D1: which workflow? Stage fixed (W-A) vs stage moves wells to the axis (W-B)

![D1 workflows](img/d1_workflows.png)

## Conclusion

If the requirement is **"pick from any of the 96 wells while watching it through the IX73"**, then **W-B is the baseline**. The IX73 stage brings the source well to the optical axis, the picker picks at the axis, and the stage then brings the destination well to the axis for an observed dispense. W-A (stage fixed, picker reaches every well) can *reach* all 96 wells but can *see* only the well on the optical axis. It observes {{D1_WA_OBSERVED}} well per stage setting, and none at all with a centred plate. W-A stays valid only if the non-axis wells are served blind or by a separate overview camera.

This is a provisional choice. **Nothing is frozen until the {{FREEZE_GATE_N}} freeze-gate items ({{FREEZE_GATE}}) are measured** (see "Freeze gate" below).

## V1 scope and acceptance (issue #10)

V1 is frozen to **one plate SKU: {{V1_PLATE_SKU}}** (96-well, round U-bottom, without lid during picking), with the {{V1_THETA:.0f}}° head ({{V1_HEAD}}). All 96-well geometry in the model (rim Ø, depth, plate height, well-bottom height, safe-Z) comes from this SKU's profile in `params.PLATE_PROFILES`. Other plates ({{EXPERIMENTAL_PLATES}}) are **experimental** and outside V1 acceptance.

**Target location.** In a U-bottom well the object settles near the bottom centre. V1 accepts a target anywhere within **{{V1_TARGET_R:.1f}} mm of the well-bottom centre**, in any direction. The binding direction is towards the far (+X) wall, where the leaning shaft is closest to the rim. For each capillary class the largest offset that still keeps the {{RIM_MARGIN}} mm rim margin is:

{{V1_TARGET_MD}}

A class that fails (allowed radius below {{V1_TARGET_R:.1f}} mm) can still pick objects that sit close to the centre, but the operator must reject off-centre targets for it; this is a known V1 limitation, not a hidden one. The measured plate lot (M19) replaces the drawing values.

## Why (numbers from the same CAD and analysis)

| | W-A stage fixed | W-B stage moves wells to the axis |
|---|---|---|
| Wells observed while picking | **{{D1_WA_OBSERVED}}** / 96 per stage setting (4× FOV ≈ {{FOV}} mm) | **{{D1_WB_OBSERVED}}** / 96 with IX3-SVR or SCAN IM |
| Dispense | blind, anywhere the picker reaches | observed, same plate (stage brings the destination to the axis) |
| Picker tip travel X × Y × Z | {{WA_TRAVEL_X}} × {{WA_TRAVEL_Y}} × {{WA_TRAVEL_Z}} mm | {{WB_TRAVEL_X}} × {{WB_TRAVEL_Y}} × {{WB_TRAVEL_Z}} mm (X {{WB_X_MIN}}…+{{WB_X_MAX}}: +X is the park / capillary-change retreat) |
| Dog-leg arm / thin section under the condenser | {{WA_ARM_L}} / {{WA_THIN_L}} mm | **{{WB_ARM_L}} / {{WB_THIN_L}} mm** (shorter, stiffer) |
| Tower axis from optical axis | +{{WA_TOWER_X}} mm | +{{WB_TOWER_X}} mm |
| Clearance sweep, R08 head, IX-ULWCD: pick / safe-Z | {{SW_WA_R08_ULWCD_PICK}}/96, {{SW_WA_R08_ULWCD_SAFE}}/96 | {{SW_WB_R08_ULWCD_PICK}}/96, {{SW_WB_R08_ULWCD_SAFE}}/96 (plate and stage translated for each well) |
| Stage-travel corners (stage moves with tip at safe-Z) | – | {{SW_WB_R08_ULWCD_STAGE_CORNER}}/{{SW_WB_R08_ULWCD_STAGE_CORNER_N}} clear |
| Min clearance at safe-Z (PH condenser) | {{SW_WA_R08_ULWCD_SAFE_CLEAR}} mm | {{SW_WB_R08_ULWCD_SAFE_CLEAR}} mm |
| Needs a motorised IX73 stage for automation | no | **yes, with ≥ 99 × 63 mm travel** |
| Extra hardware for observation | an overview camera for the non-axis wells | none |

**Stage requirement for W-B.** The plate's well span is 99 × 63 mm, so the stage must shift the plate by at least ±49.5 × ±31.5 mm:

| Stage | Travel (mm) | Motorised | Wells it can bring to the axis |
|---|---|---|---|
| IX3-SVR (manual, S02) | 114 × 75 | no | {{D1_WB_SVR_WELLS}}/96 (operator moves it: semi-automatic only) |
| IX3-SSU (Evident ultrasonic, S01) | 76 × 52 | yes | **{{D1_WB_SSU_WELLS}}/96: insufficient** |
| Märzhäuser SCAN IM for IX73 (S15) | 120 × 80 | yes | {{D1_WB_SCANIM_WELLS}}/96 |

Evident's own ultrasonic IX3-SSU stage **cannot** bring the outer columns and rows to the axis. A W-B automation therefore needs a third-party (or other Evident) motorised stage in the 120 × 80 mm class, such as the Märzhäuser SCAN IM (2 mm pitch ball screw, per S15), or a semi-automatic mode on the manual IX3-SVR.

## Consequences of choosing W-B

1. **The picker becomes a local manipulator.** Its travel falls to {{WB_TRAVEL_X}} × {{WB_TRAVEL_Y}} × {{WB_TRAVEL_Z}} mm, and the arm shortens from {{WA_ARM_L}} to {{WB_ARM_L}} mm. The frame, the Y beam and the X cantilever all get smaller, and moving mass drops, mostly on Y. The dog-leg under the IX-ULWCD is still needed, because the pick still happens on the optical axis.
2. **Plate and stage load.** The picker never touches the stage. The motorised stage carries only the plate, well within its rating (IX3-SVR: max 1000 g, S02; check the chosen motorised stage).
3. **Sequence.** Stage: source well → axis. Z: land at about 10 µm/s and pick. Z: rise to safe-Z ({{SAFE_Z:.2f}} mm). Stage: destination well → axis. Z: land and expel. Z: safe-Z. **The stage moves only with the tip inside the safe-Z corridor** ({{CORR_R08_LO:.2f}}–{{CORR_R08_HI:.2f}} mm for the V1 head, `03_architecture.md` §5); the sweep confirms this is clear at all stage-travel corners. Moving it with the tip at pick height drags the capillary through the plate.
4. **Calibration** simplifies. The pick point is always the optical axis, so image → picker mapping needs only a local 3-point calibration around the axis (SpheroidPicker method, S28). Well positions come from the stage coordinates.
5. **Destination on another plate.** Two plates do not fit within the stage travel. Transfers between plates need either a plate change, or a hybrid (W-C, not modelled) where the picker carries the object at safe-Z to a fixed destination station beside the stage. W-C brings back W-A's long X travel for that one move.
6. **Throughput.** Each transfer adds two stage moves (about 1–2 s each at typical 20–50 mm/s stage speeds; to be confirmed for the chosen stage). The landings take longer. At 10 µm/s, a 50 µm slow zone costs 5 s per landing, or about 10 s per transfer. The SpheroidPicker also dwells 7 s before its pick pulse (S28). One transfer therefore takes roughly 20–30 s, which is acceptable for spheroid picking. The landings, not the stage, set the pace.

## When W-A is still the better choice

- There is no budget or space for a motorised stage, the source objects sit only in a few wells placed near the axis, and destinations can be served blind.
- A separate overview camera can image the whole plate from above (off-axis, outside the condenser keep-out), giving target coordinates for blind picking. That trades the IX73's optical quality at the pick for coverage.

## Freeze gate

The following must be measured and entered in `cad/params.py` before any part number or bracket is frozen. The model, the sweep and these documents then re-render automatically (`python tools/build_all.py`).

| Measurement | Decides |
|---|---|
| M1 stage-top height above table | frame height |
| M3 stage outline, clips; M4 stage centre vs axis | clearance to the moving plate (W-B) |
| M6 condenser model and diameter; M7 carrier arm; M8 real condenser front height | the thin-arm length, and every clearance currently at ~5 mm |
| M10 tilted-column envelope | fallback without condenser |
| M15 free table space right of the IX73 | tower placement |
| M19 V1 plate lot ({{V1_PLATE_SKU}}): rim Ø, depth, height, A1 position | V1 acceptance, safe-Z lower bound |
| M23 head height above the collet nose (V1 holder, tubing clipped) | safe-Z corridor upper bound, condenser margin |
| (W-B) choice and envelope of the motorised stage (SCANplus IM dimension sheet S37 not yet retrieved) | stage travel ≥ 99 × 63, frame height above the insert, clearance to the tower |

W-B also needs the stage travel centre within the centring allowance of `03_architecture.md` §5b (M4).

The clearances of {{SW_WA_R08_ULWCD_SAFE_CLEAR}}–5 mm reported by the model involve placeholder condenser geometry (a conservative Ø{{COND_D:.0f}} cylinder, `COND_PROFILE`) and placeholder IX73 placement. **They are provisional and are not design evidence yet.** No official IX73 or condenser drawing could be retrieved (source manifest S05, S06, S37).
