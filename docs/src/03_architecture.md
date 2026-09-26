# Recommended overall architecture (stage 1, not frozen)

## 1. Recommendation

**Provisional baseline (after D1, see `09_workflow_D1.md`): workflow W-B.** The IX73 stage (motorised, ≥ 99 × 63 mm travel) brings each source and destination well to the optical axis, and the picker works locally at the axis.

The picker itself is a **side tower on the right of the IX73, bolted to the optical table**:

- a fixed Y beam on two posts;
- a Y stage carrying a cantilevered X stage;
- the X stage carrying the Z stage;
- the Z stage carrying a thin dog-leg arm that reaches under an IX-ULWCD condenser to a near-vertical (8°) capillary.

The same frame concept serves W-A (stage fixed) with longer travel and a longer arm. Both are kept in the model. The numbers below are for **W-B unless marked W-A**.

It is the cleanest robust layout for three reasons, each backed by the model:

1. **Only one thin element enters the optical-axis zone.** The arm is {{ARM_T_TXT}} for its first {{WB_THIN_L}} mm (W-A: {{WA_THIN_L}} mm). The tall Z actuator stays outside the condenser keep-out in every position, and the moving system clears the IX-ULWCD at all 96 wells at pick height and at safe-Z in both workflows (`09_workflow_D1.md`, `generated_analysis_tables.md`).
2. **The frame avoids every side of the IX73 that is used or unknown.** The operator side and eyepieces (front), the illumination pillar and lamp (rear) and the camera port (left, assumed) all stay clear. The tower axis is {{WB_GAP:.0f}} mm clear of the body side (W-A: {{WA_GAP:.0f}} mm), and nothing touches the microscope or its stage.
3. **The stiff, fixed parts are the long ones.** The Y beam is supported at both ends. The cantilevers are the X support beam and the arm ({{WB_ARM_L}} mm in W-B, {{WA_ARM_L}} mm in W-A). Both deflect repeatably, and the image calibration absorbs the static sag.

**Nothing here is frozen** until M1, M3, M4, M6, M7, M8, M10 and M15 are measured (`09_workflow_D1.md`, freeze gate).

## 2. What is fixed and what moves

| Item | Group | Mounted on | Moves with | Mass carried (estimate, ±30 %) |
|---|---|---|---|---|
| Optical table, IX73, stage, plate, condenser | fixed | – | – | – |
| Base plate (15 mm Al), 2 posts (80 × 80), Y beam (80 × 80), diagonal braces | fixed | table | – | – |
| Y actuator body + motor + home switch, Y cable chain, tubing fixed clamp | fixed | Y beam | – | – |
| Y carriage, X support beam (40 × 80 min.), X actuator + motor + switch, X cable chain | **Y** | Y carriage | Y | **Y axis moves ≈2.5–3.0 kg (W-B), ≈3.0–3.5 kg (W-A)** |
| X carriage bracket, Z actuator + motor + top home switch, tubing clamp #2 | **X** | X carriage | X, Y | **X axis moves ≈1.2–1.4 kg** |
| Z carriage, kinematic break-away mount, dog-leg arm, collet holder, capillary, first 0.3 m of tubing | **Z** | Z carriage | X, Y, Z | **Z axis moves ≈0.25–0.35 kg** |
| Syringe pump (Harvard/Tecan), controller, 24 V PSU | fixed, off-frame | table/shelf | – | – |

The masses are estimates for width-20–26 class ball-screw stages with NEMA17 motors. They are not catalogue values and must be recomputed once part numbers are chosen.

## 3. Axis stacking and travel

Order from the table up: **Y (fixed on beam) → X (cantilever towards the axis) → Z (vertical) → arm → holder → capillary.**

| Axis | W-B stroke | W-A stroke | Why |
|---|---|---|---|
| X | **{{WB_TRAVEL_X}} mm** (tip {{WB_X_MIN}}…+{{WB_X_MAX}}) | {{WA_TRAVEL_X}} mm | W-B: local calibration ±15 mm plus park / capillary change outside the condenser keep-out. W-A: 99 mm well span + 25.5 mm per side |
| Y | **{{WB_TRAVEL_Y}} mm** | {{WA_TRAVEL_Y}} mm | W-B: local calibration. W-A: 63 mm span + 18.5 mm per side |
| Z | **{{WB_TRAVEL_Z}} mm** | {{WA_TRAVEL_Z}} mm | pick height {{Z_PICK:.2f}} → safe-Z {{SAFE_Z:.2f}} → top: capillary change and calibration touch-off |

Why Y is the fixed axis and X the cantilever: the side tower gives a naturally long, twice-supported beam in Y. X must reach from the tower to the plate anyway. Swapping them would cantilever the *fixed* beam over the microscope.

## 4. Reaching all 96 wells

- **W-B (baseline).** The stage brings each well to the axis. With the IX3-SVR or a 120 × 80 motorised stage, all 96 wells can be picked *and observed*. The sweep translates plate and stage for every well: {{SW_WB_R08_ULWCD_PICK}}/96 clear at pick height, {{SW_WB_R08_ULWCD_SAFE}}/96 at safe-Z. The stage moves only with the tip at safe-Z. The IX3-SSU (76 × 52) reaches only {{D1_WB_SSU_WELLS}}/96.
- **W-A.** Tip travel {{WA_TRAVEL_X}} × {{WA_TRAVEL_Y}} covers the 99 × 63 mm well field ({{SW_WA_R08_ULWCD_PICK}}/96 in the sweep), but only {{D1_WA_OBSERVED}} well is observed per stage setting. The rest are picked or dispensed blind unless an overview camera is added.

## 5. Z axis: low backlash and no drop on power loss

- **Screw.** Ball screw, lead 1 mm (THK KR20 class, S30), or TR8×2 *single-start, 2 mm lead* in the fallback architecture. Never the common Tr8×8(P2) four-start (8 mm lead), which can back-drive under load (S35).
- **Holding without power.** Back-driving torque from the Z load is T = F·l·η/(2π). With F ≈ 3 N (0.3 kg), l = 1 mm and η ≈ 0.8, T ≈ 0.4 mN·m. A NEMA17's unpowered detent torque is typically about 10–20 mN·m (catalogue class, to be confirmed for the chosen motor), a margin of roughly 25–50×. With a TR8×2 bronze nut, the lead angle (≈5.2° at 7 mm pitch diameter) is below the friction angle (≈6–11° for μ = 0.1–0.2), so the screw is nominally self-locking. Vibration can still creep a marginal self-locking screw.
- **Conclusion.** No brake and no counterbalance are needed at this Z load. Add a brake (for example the Oriental DRS2 brake option, S32) only if the Z group grows above about 0.5 kg or if a lead ≥2 mm ball screw is chosen.
- **Resolution.** 1 mm lead / 200 full steps = 5 µm per full step, and 16× microstepping gives 0.31 µm commanded increments. Microstep linearity limits real incremental accuracy to a fraction of a full step, which is sufficient for the ≤5 µm command and 10–20 µm repeatability targets.
- **Approach.** Move fast to safe-Z ({{SAFE_Z:.2f}}), then to a pre-contact height about 0.5 mm above the stored well bottom, then land at about 10 µm/s (S23) to the stand-off height.

## 6. Capillary holder concept

The holder is a **collet** (split collet with a tapered nut, sized per capillary OD) in a Ø10 × 14 mm envelope, with these features:

- A screw-set **depth stop** above the capillary gives adjustable insertion (default 10 mm grip, 30 mm exposed).
- A side or top liquid port with an O-ring seal on the capillary end-face. The seal is separate from the clamping, so it does not act as friction-only clamping.
- The holder sits in a **V-block seat on the arm** with a flat and a clamp screw. This is the mechanically defined reference surface.
- **Angle** is set by an exchangeable angle block ({{ANGLE_BLOCKS_TXT}}) between the kinematic mount and the holder seat: two dowels and one clamp screw. Each plate format has its own block and exposed length (`10_plate_formats_angle_blocks.md`).
- **Tip reproducibility.** The collet and depth stop give roughly ±0.1–0.2 mm (estimate). The real µm-level registration comes from the image-based 3-point re-calibration after every change (S28). The mechanics therefore need only be *stable after clamping*, not µm-reproducible between capillaries.
- **Other ODs**: objects of 100 µm – 1 mm need three capillary classes (OD 1.0 / 1.5 / 2.0; see `08_capillary_sizing.md`). They are handled by swapping the collet insert only, and all keep ≥0.87 mm rim clearance at 8°. The arm, seat and fluid port stay the same.

Commercial alternative: a patch-clamp-style pipette holder with a side port (for example, the Warner holder catalogue in the search results). Many of these clamp with O-rings, which is friction-only and was rejected as the primary fixation. One can be used with a custom depth-stop adapter.

## 7. Tubing and cable routing

**Tubing.** Use PTFE/FEP 1/16" OD (bore to suit, liquid-filled), with no drag chain. Route:

1. Holder top → along the side of the arm, in a clip groove, not on top (it is the closest item to the condenser).
2. Clamp #1 on the Z carriage.
3. Z service loop to clamp #2 on the Z body (X group).
4. X/Y service loop, hung from the X support beam, to the fixed clamp on the frame post.
5. Down the post to the pump on the table (about 1.2 m in total).

Each loop takes the full stroke with a bend radius of at least 25 mm (PTFE kink limit; to be checked for the chosen tubing). Keep the pump, any pinch valve and any pressure tee on the fixed side.

**Cables.** X/Y/Z motor and switch cables leave on the rear (+Y) side of the moving groups and run in two small cable chains (X on the Y group, Y on the frame). That keeps them physically separated from the tubing, which runs on the front (−Y) side. Motor cables should be shielded and separate from the switch cables in the chain.

## 8. Alternatives considered

| Alternative | Verdict | Reason |
|---|---|---|
| Front bridge (beam along X in front of the stage) | rejected | Sits in the eyepiece / observation-tube envelope and the operator's hand space. The eyepiece position is unknown (M12). |
| Rear bridge | rejected | The illumination pillar and lamp housing occupy the rear. |
| Full gantry over the microscope | rejected | The beam must pass above the condenser carrier, which makes Z very long and compliant. |
| Straight holder (no dog-leg) at 30–45° | rejected | Cannot reach 96-well bottoms (`02_…`). |
| **Motorised IX73 stage + short-travel picker (W-B)** | **baseline** | Follows the CellSorter/NanoPick pattern (S22, S24). Every pick and dispense is observed; smaller and stiffer; needs a motorised stage ≥ 99 × 63 mm (not the IX3-SSU). |
| Stage fixed, picker covers the plate (W-A) | kept as alternative | Reaches all wells but observes only the one on the axis; needs an overview camera or blind operation. |
| Pillar tilted back + vertical capillary + fixed LED ring illumination | valid fallback | Removes the condenser conflict entirely. It costs Köhler brightfield during the pick and needs an LED mounted on the frame, not on the head. |

## 9. Alignment and locking interfaces (custom parts that add value)

- **Base plate to table.** Slotted holes on the table grid (M6/25 mm or ¼-20/1", M16). Gives ±15 mm X/Y and ±2° yaw, locked with 6 bolts.
- **Beam height on posts.** Vertical slots plus a jack screw give ±20 mm to match the real stage height (M1). Two clamp bolts per post.
- **X-axis squareness to the plate rows.** Not adjusted mechanically; absorbed by the image calibration (affine transform).
- **Capillary angle.** Exchangeable angle blocks ({{ANGLE_BLOCKS_TXT}}), doweled; re-calibrate by image after each change.
- **Removability.** Unbolt the base plate: the IX73 is untouched and its alignment unchanged. Re-installing needs only re-running the image calibration.

## 10. Answers to the system-level questions

| Question | Answer (model reference pose) |
|---|---|
| Where does the gantry sit relative to the IX73? | Right-hand side; tower axis at x = +{{WB_TOWER_X}} mm (W-A: +{{WA_TOWER_X}}) from the optical axis; posts at y = {{WB_POST_Y0}} and +{{WB_POST_Y1}} mm (W-A: {{WA_POST_Y0}} / +{{WA_POST_Y1}}); on its own base plate on the table. |
| Which parts move / stay fixed? | §2 table. The plate and stage move in W-B, driven by the IX73 stage, not by the picker. |
| Moving mass per axis? | Y ≈2.5–3.0 kg (W-B) / 3.0–3.5 kg (W-A), X ≈1.2–1.4 kg, Z ≈0.25–0.35 kg (estimates). |
| How does it reach all 96 wells? | W-B: the stage brings each well to the axis ({{D1_WB_OBSERVED}}/96 observed). W-A: picker travel {{WA_TRAVEL_X}} × {{WA_TRAVEL_Y}} ({{D1_WA_OBSERVED}} observed). |
| Where does the capillary enter the plate? | Vertically from above with an 8° lean towards +X. The holder nose stays ≈19 mm above the plate top at pick height. |
| Where does the tubing leave the head? | Holder top → side of the arm → clamp on the Z carriage (outboard, x ≈ tip + {{WB_ARM_L}} mm). |
| Likely collision regions? | Condenser front (arm and tubing, {{SW_WB_R08_ULWCD_SAFE_CLEAR}} mm at safe-Z with a placeholder condenser); condenser carrier arm vs X support beam (placeholder); well rims (angle); lid; in W-B, the plate moving under the tip if the stage moves below safe-Z. |
| How does the condenser constrain the angle? | Indirectly: the wells force near-vertical, so the capillary must sit below the condenser. That needs WD ≥ about 65 mm (IX-ULWCD) or the column tilted back. |
| Free space needed around the microscope? | Right side: from the body side (x = {{IX73_HALF_W}}) to x ≈ +{{WB_FOOT_X}} (W-B) / +{{WA_FOOT_X}} (W-A) for the frame, plus the pump and controller beyond, if placed there. Nothing on the front, left or rear. |
| Which dimensions still need measuring? | Freeze gate: M1, M3, M4, M6, M7, M8, M10, M15 (`05_measurement_checklist.md`). |
