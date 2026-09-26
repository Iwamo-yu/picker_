# Recommended overall architecture (stage 1, not frozen)

## 1. Recommendation

**Build a side tower on the right of the IX73, bolted to the optical table. A fixed Y beam is carried on two posts. The Y stage carries a cantilevered X stage, the X stage carries the Z stage, and the Z stage carries a thin dog-leg arm that reaches under an IX-ULWCD condenser to a near-vertical (8°) capillary.**

It is the cleanest robust layout for three reasons, each backed by the model:

1. **Only one thin element enters the optical-axis zone.** The arm is 12 × 12 mm for its first 120 mm. The tall Z actuator stays ≥55 mm off the axis in every position, and the whole moving system clears the IX-ULWCD at all 96 wells at pick height and at safe-Z (`02_approach_angle_study.md`).
2. **The frame avoids every side of the IX73 that is used or unknown.** The operator side and eyepieces (front), the illumination pillar and lamp (rear) and the camera port (left, assumed) all stay clear. The tower axis is 238 mm clear of the body side, and nothing touches the microscope or its stage.
3. **The stiff, fixed parts are the long ones.** The Y beam is supported at both ends. The only cantilevers are the X support beam (≤285 mm, carrying ≈1.3 kg) and the arm (≤175 mm, carrying ≈0.05 kg). Both deflect repeatably, so the image calibration absorbs the static sag.

## 2. What is fixed and what moves

| Item | Group | Mounted on | Moves with | Mass carried (estimate, ±30 %) |
|---|---|---|---|---|
| Optical table, IX73, stage, plate, condenser | fixed | – | – | – |
| Base plate (15 mm Al), 2 posts (80 × 80), Y beam (80 × 80), diagonal braces | fixed | table | – | – |
| Y actuator body + motor + home switch, Y cable chain, tubing fixed clamp | fixed | Y beam | – | – |
| Y carriage, X support beam (40 × 80 min.), X actuator + motor + switch, X cable chain | **Y** | Y carriage | Y | **Y axis moves ≈3.0–3.5 kg** |
| X carriage bracket, Z actuator + motor + top home switch, tubing clamp #2 | **X** | X carriage | X, Y | **X axis moves ≈1.2–1.4 kg** |
| Z carriage, kinematic break-away mount, dog-leg arm, collet holder, capillary, first 0.3 m of tubing | **Z** | Z carriage | X, Y, Z | **Z axis moves ≈0.25–0.35 kg** |
| Syringe pump (Harvard/Tecan), controller, 24 V PSU | fixed, off-frame | table/shelf | – | – |

The masses are estimates for width-20–26 class ball-screw stages with NEMA17 motors. They are not catalogue values and must be recomputed once part numbers are chosen.

## 3. Axis stacking and travel

Order from the table up: **Y (fixed on beam) → X (cantilever towards the axis) → Z (vertical) → arm → holder → capillary.**

| Axis | Stroke | Why this value | Direction |
|---|---|---|---|
| X | **150 mm** | 99 mm well span (A1–A12) + 25.5 mm per side for retreat, calibration and park | operator's left–right, along the plate's long side |
| Y | **100 mm** | 63 mm span (A–H) + 18.5 mm per side | front–back |
| Z | **50 mm** | pick height 3.35 → safe-Z 19.35 (+16) → top 50.35: room for capillary change and calibration touch-off | vertical |

Why Y is the fixed axis and X the cantilever: the side tower gives a naturally long, twice-supported beam in Y. X must reach from the tower to the plate anyway. Swapping them would cantilever the *fixed* beam over the microscope.

## 4. Reaching all 96 wells

At the reference stage position (plate centred on the optical axis), tip travel ±75 × ±50 mm covers the 99 × 63 mm well field with the margins above (`img/dim_top.png`). The sweep confirms 96/96 wells at pick height and at safe-Z with the IX-ULWCD or with the column tilted back.

**Workflow caveat.** The picker works in the table frame. Only the well above the objective is imaged, so moving the IX73 stage moves the plate relative to the picker. There are two consistent workflows:

- **(a) Stage locked at the reference position.** Pick under vision only in wells near the optical axis. Dispense anywhere on the plate "blind" (target positions come from the plate geometry and one calibration). This is what the 150 × 100 travel is sized for.
- **(b) Stage moves each source well over the objective.** The picker then picks at the axis. The destination must be known in stage coordinates, which needs either a motorised/encoded stage or an operator-confirmed stage position. X/Y reach of the destination shrinks by the stage offset: with source well A1 over the axis, column 12 of the same plate is out of reach.

This choice (**D1**) decides whether the IX73 needs a motorised stage. It does not change the frame, but it changes the travel needed and the software.

## 5. Z axis: low backlash and no drop on power loss

- **Screw.** Ball screw, lead 1 mm (THK KR20 class, S30), or TR8×2 *single-start, 2 mm lead* in the fallback architecture. Never the common Tr8×8(P2) four-start (8 mm lead), which can back-drive under load (S35).
- **Holding without power.** Back-driving torque from the Z load is T = F·l·η/(2π). With F ≈ 3 N (0.3 kg), l = 1 mm and η ≈ 0.8, T ≈ 0.4 mN·m. A NEMA17's unpowered detent torque is typically about 10–20 mN·m (catalogue class, to be confirmed for the chosen motor), a margin of roughly 25–50×. With a TR8×2 bronze nut, the lead angle (≈5.2° at 7 mm pitch diameter) is below the friction angle (≈6–11° for μ = 0.1–0.2), so the screw is nominally self-locking. Vibration can still creep a marginal self-locking screw.
- **Conclusion.** No brake and no counterbalance are needed at this Z load. Add a brake (for example the Oriental DRS2 brake option, S32) only if the Z group grows above about 0.5 kg or if a lead ≥2 mm ball screw is chosen.
- **Resolution.** 1 mm lead / 200 full steps = 5 µm per full step, and 16× microstepping gives 0.31 µm commanded increments. Microstep linearity limits real incremental accuracy to a fraction of a full step, which is sufficient for the ≤5 µm command and 10–20 µm repeatability targets.
- **Approach.** Move fast to safe-Z (19.35), then to a pre-contact height about 0.5 mm above the stored well bottom, then land at about 10 µm/s (S23) to the stand-off height.

## 6. Capillary holder concept

The holder is a **collet** (split collet with a tapered nut, sized per capillary OD) in a Ø10 × 14 mm envelope, with these features:

- A screw-set **depth stop** above the capillary gives adjustable insertion (default 10 mm grip, 30 mm exposed).
- A side or top liquid port with an O-ring seal on the capillary end-face. The seal is separate from the clamping, so it does not act as friction-only clamping.
- The holder sits in a **V-block seat on the arm** with a flat and a clamp screw. This is the mechanically defined reference surface.
- **0–12° tilt adjustment** is made once, at the kinematic mount block (an arc slot with a lock screw).
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
| **Motorised IX73 stage + short XY (±15 mm) + Z picker** | **valid alternative** | Follows the CellSorter/NanoPick pattern (S22, S24). It is smaller and stiffer, but needs a motorised stage and still needs the dog-leg / ULWCD solution. Decide with D1. |
| Pillar tilted back + vertical capillary + fixed LED ring illumination | valid fallback | Removes the condenser conflict entirely. It costs Köhler brightfield during the pick and needs an LED mounted on the frame, not on the head. |

## 9. Alignment and locking interfaces (custom parts that add value)

- **Base plate to table.** Slotted holes on the table grid (M6/25 mm or ¼-20/1", M25). Gives ±15 mm X/Y and ±2° yaw, locked with 6 bolts.
- **Beam height on posts.** Vertical slots plus a jack screw give ±20 mm to match the real stage height (M1). Two clamp bolts per post.
- **X-axis squareness to the plate rows.** Not adjusted mechanically; absorbed by the image calibration (affine transform).
- **Capillary angle.** 0–12° arc slot at the kinematic mount, set once.
- **Removability.** Unbolt the base plate: the IX73 is untouched and its alignment unchanged. Re-installing needs only re-running the image calibration.

## 10. Answers to the system-level questions

| Question | Answer (model reference pose) |
|---|---|
| Where does the gantry sit relative to the IX73? | Right-hand side; tower axis at x = +400 mm from the optical axis; posts at y = −150 and +230 mm; on its own base plate on the table. |
| Which parts move / stay fixed? | §2 table. |
| Moving mass per axis? | Y ≈3.0–3.5 kg, X ≈1.2–1.4 kg, Z ≈0.25–0.35 kg (estimates). |
| How does it reach all 96 wells? | Tip travel 150 × 100 covers 99 × 63 plus margins; 96/96 in the sweep (IX-ULWCD). |
| Where does the capillary enter the plate? | Vertically from above, 8° lean towards +X; the holder nose stays ≈19 mm above the plate top at pick height. |
| Where does the tubing leave the head? | Holder top → side of the arm → clamp on the Z carriage (outboard, x ≈ tip + 150 mm). |
| Likely collision regions? | Condenser front (arm/tubing, 4.8 mm at safe-Z), condenser carrier arm vs X support beam (5 mm, placeholder), well rims (angle), lid. |
| How does the condenser constrain the angle? | Indirectly: the wells force near-vertical, so the capillary must sit below the condenser. That needs WD ≥ about 65 mm (IX-ULWCD) or the column tilted back. |
| Free space needed around the microscope? | Right side: from the body side (x = 161.5) to x = +496 for the frame, plus the pump/controller to about x = +760 if placed there. Depth y = −220 … +300. Height: up to +251 mm above the stage top (Z motor). Nothing on the front, left or rear. |
| Which dimensions still need measuring? | `05_measurement_checklist.md`: M1, M6–M8 and M12 first. |
