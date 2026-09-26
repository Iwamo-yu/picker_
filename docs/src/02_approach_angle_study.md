# Capillary approach: 0° vs 8° vs 30° vs 45°, plus collision and interference notes

Figures: `img/approach_angles.png`, `img/view_head.png`, `img/dim_front.png`. The raw numbers are in `generated_analysis_tables.md`, produced by `cad/analysis.py`.

## Conclusion

The capillary's last segment must be **near-vertical (0–12°)**. The binding constraint is the 96-well itself, not the condenser. A near-vertical capillary then has to share the space on the optical axis with the condenser. That works only if (a) the condenser has a long working distance (IX-ULWCD, WD 73 mm) and the picker reaches in with a thin horizontal "dog-leg" arm below it, or (b) the illumination column is tilted back during picking. With the IX2-LWUCD (WD 27 mm) no angle works. **8° with a dog-leg arm** is the recommended geometry for 96-well plates. The angle is set by exchangeable angle blocks ({{ANGLE_BLOCKS_TXT}}), one per plate format (`10_plate_formats_angle_blocks.md`), not by a continuous tilt.

## Method

Every angle uses the same external frame and the same outboard Z position, with the W-A frame ({{WA_ARM_L}} mm arm, picker covering the plate; the W-B frame gives the same angle results at the optical axis). Only the capillary/holder angle changes, so the comparison isolates the effect of angle. Three checks were run:

1. **Well access (analytic).** Corning 7007 U-bottom: rim Ø6.86 mm, depth 11.30 mm (S13). Capillary OD 1.0 mm, tip 0.3 mm above the well bottom.
2. **Clearance sweep (OpenCascade minimum distance).** All 96 wells at pick height and at safe-Z (the lower bound of the safe-Z corridor: highest moving plate or clip feature + {{CORRIDOR_LOWER_MARGIN:.0f}} mm), plus a 35-point grid over the full 150 × 100 travel at safe-Z and at the top of the Z stroke. Moving parts are checked against the IX73 envelope, the condensers, the plate and the pump.
3. **Illumination obstruction (analytic).** Fraction of the condenser light cone blocked by the Ø10 holder at its nose height.

## Results

| Criterion | 0° | **8° (rec.)** | 30° | 45° |
|---|---|---|---|---|
| Rim clearance, tip at well-bottom centre | +{{RIM_0:.2f}} mm | **+{{RIM_8:.2f}} mm** | {{RIM_30:.2f}} mm (hits rim) | {{RIM_45:.2f}} mm (hits rim) |
| Deepest centred reach below the rim | full (11.3 mm) | **full** | {{REACH_30:.1f}} mm | {{REACH_45:.1f}} mm |
| Wells reachable at pick height, IX-ULWCD | {{SW_WA_V00_ULWCD_PICK}}/96 | **{{SW_WA_R08_ULWCD_PICK}}/96** | {{SW_WA_V30_ULWCD_PICK}}/96 | {{SW_WA_V45_ULWCD_PICK}}/96 |
| Wells reachable at pick height, IX2-LWUCD | {{SW_WA_V00_LWUCD_PICK}}/96 | {{SW_WA_R08_LWUCD_PICK}}/96 | {{SW_WA_V30_LWUCD_PICK}}/96 | {{SW_WA_V45_LWUCD_PICK}}/96 |
| Wells reachable at pick height, pillar tilted back | {{SW_WA_V00_NONE_PICK}}/96 | **{{SW_WA_R08_NONE_PICK}}/96** | {{SW_WA_V30_NONE_PICK}}/96 | {{SW_WA_V45_NONE_PICK}}/96 |
| Illumination blocked by holder, condenser NA 0.1 / 0.3 | 100 % / 28 % | 61 % / 28 % | 0 % / 0 % | 0 % / 0 % |
| Tip visible beside holder in transmitted light | no (coaxial) | partly | yes | yes |
| Cantilever from holder to tip (exposed glass) | 30 mm | 30 mm | 30 mm | 30 mm |
| Lateral tip compliance from tubing/drag forces | lowest | low | medium (bending ∝ sin θ) | highest |
| Tubing exit | vertical, turns into arm | same | along capillary axis, higher | lowest, near plate |
| Maximum angle for bottom-centre access | | {{MAX_ANGLE:.1f}}° (no margin) | | |

**Reading the table.**

- **30° and 45° fail** for any standard 96-well plate. The shaft meets the rim long before the tip reaches the bottom. That holds whatever condenser is fitted. An angled capillary also cannot follow an object off-centre on the far side of a U-bottom.
- **0° is geometrically best** for the wells, but the holder sits coaxially above the tip. At low condenser NA it blocks the whole light cone, so transmitted-light imaging during the landing is lost.
- **8°** keeps a {{RIM_8:.2f}} mm rim margin and moves the holder about 4 mm off the axis. Including the arm, the head still blocks about a third of the NA 0.3 cone at 8° (ray test, `generated_analysis_tables.md` §2), so the image is darker during landing but the tip remains visible beside the holder. The Zhao et al. 45° mount (S23) is correct for open droplets but not for wells.

The illumination figures are an obstruction estimate, not an optical simulation. **Test M18** (a Ø10 rod at 30–45 mm above focus, 4× and 10×) decides whether the 8° block is enough for 96-well work or whether a 10–12° block should be added.

## Condenser constraint

Condenser fronts are placed at well bottom + WD, with WD from manufacturer data (S03, S04). Condenser diameter and body are **placeholders** (Ø80), so all numbers below move once M6–M8 are measured.

| Condenser | WD (MFR) | front above plate top | Result with dog-leg arm (12 mm thick) |
|---|---|---|---|
| IX2-LWUCD | 27 mm | ≈15.7 mm | arm collides at pick height near the axis: **unusable** |
| IX2-MLWCD | 45 mm | ≈33.7 mm | arm collides at pick height near the axis: **unusable** |
| **IX-ULWCD** | 73 mm | ≈61.7 mm | W-A {{SW_WA_R08_ULWCD_PICK}}/96, W-B {{SW_WB_R08_ULWCD_PICK}}/96 at pick height; minimum clearance {{SW_WA_R08_ULWCD_SAFE_CLEAR}} mm at safe-Z (tubing on the arm vs condenser front) |
| none (column tilted back) | – | – | no constraint; needs alternative illumination during picking |

## Collision and interference notes

1. **Condenser.** This is the dominant hazard. Under the IX-ULWCD the Z stroke **above the reference height is blocked near the axis**. W-A: {{SW_WA_R08_ULWCD_GRID_TOP}} of 35 grid points at top-Z are clear; W-B: {{SW_WB_R08_ULWCD_GRID_TOP}} of 35. In W-A the arm reaches 120 mm towards +X, so collisions also occur with the tip *outside* a simple cylinder around the axis. The control rule is therefore: **Z may go above the reference switch height only at the park position** (X ≥ park), and homing lifts Z to the reference switch first (`06_electrical.md`). Capillary changes happen at park.
2. **Arm length.** The thin section of the arm must extend from the tip by |tip x min| + condenser radius + margin: {{WA_THIN_L}} mm in W-A, {{WB_THIN_L}} mm in W-B (computed in `params.layout`). (During the W-A iteration, a 60 mm thin section collided at safe-Z in columns 1–3. The sweep caught it, and the rule above was derived from it.) The tall Z actuator stays outboard of the condenser in every position.
3. **Tubing on the arm.** It is the closest item to the condenser ({{SW_WA_R08_ULWCD_SAFE_CLEAR}} mm). Route it along the side of the arm, not on top.
4. **Well walls.** They are the binding constraint on angle (above). The OCC sweep and the analytic check agree: 30° and 45° give {{SW_WA_V30_ULWCD_PICK}}/96.
5. **Plate lid.** The model assumes no lid. A lid adds about 2 mm (Corning 7007 is 0.650 in = 16.5 mm high with lid, against 14.35 mm without). Lid removal belongs in the workflow.
6. **Stage and plate holder clips.** These are unknown (M3). The arm underside is ≈41 mm above the stage at pick height and ≈57 mm at safe-Z, so it is not critical.
7. **Objective and turret.** They lie below the stage; the picker cannot reach them because nothing moves below z = 0. The risk is to the plate bottom, not the objective: a tip driven through a thin plate bottom would load the plate. Limit this with a firmware Z floor at the **measured** well bottom + r·sin θ + 0.1 mm per plate × block × capillary class (the lowest edge of a tilted square-cut tip), never below the bottom.
8. **Microscope frame.** The closest fixed IX73 item to the frame is the body side at x = +161.5 mm. The tower axis is at +{{WA_TOWER_X}} mm in W-A ({{WA_GAP:.0f}} mm gap) and +{{WB_TOWER_X}} mm in W-B ({{WB_GAP:.0f}} mm gap). The X support beam passes over the stage at z ≥ 180 mm; the condenser carrier arm is at x = ±45 mm (placeholder), and the X actuator's inner end is at x = {{WA_X_LO}} mm ({{WA_X_INNER_CLEAR}} mm beyond the condenser radius). **This gap is a placeholder result and must be re-checked after M7.**
9. **Eyepieces / observation tube.** The frame does not use the operator side. A front bridge was rejected because it would sit in the (unknown, M12) eyepiece envelope and in the operator's hand space.
10. **Collision fuse.** The arm hangs on a magnet-preloaded kinematic mount (e.g. Thorlabs KB25/M, about {{BREAKAWAY_HOLD_N:.0f}} N holding force, P12). It is a **kinematic repositioner, not a force limiter**: its release force at the tip is about {{BREAK_RELEASE_N:.2f}} N. That protects the plate, stage and condenser from a stalled axis (below the {{PLATE_FORCE_LIMIT:.0f}} N plate limit, placeholder), but **not the capillary**, whose estimated lateral breaking force is {{BREAK_MIN_N:.2f}}–{{BREAK_MAX_N:.2f}} N (`06_electrical.md`). Treat capillaries as consumables in a crash, and re-calibrate after any detach. A compliant low-force stage at the holder is open decision D9.
