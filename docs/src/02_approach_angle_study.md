# Capillary approach: 0° vs 8° vs 30° vs 45°, plus collision and interference notes

Figures: `img/approach_angles.png`, `img/view_head.png`, `img/dim_front.png`. The raw numbers are in `generated_analysis_tables.md`, produced by `cad/analysis.py`.

## Conclusion

The capillary's last segment must be **near-vertical (0–12°)**. The binding constraint is the 96-well itself, not the condenser. A near-vertical capillary then has to share the space on the optical axis with the condenser. That works only if (a) the condenser has a long working distance (IX-ULWCD, WD 73 mm) and the picker reaches in with a thin horizontal "dog-leg" arm below it, or (b) the illumination column is tilted back during picking. With the IX2-LWUCD (WD 27 mm) no angle works. **8° with a dog-leg arm** is the recommended fixed geometry, with an alignment range of about 0–12°.

## Method

Every angle uses the same external frame and the same outboard Z position, with the W-A frame ({{WA_ARM_L}} mm arm, picker covering the plate; the W-B frame gives the same angle results at the optical axis). Only the capillary/holder angle changes, so the comparison isolates the effect of angle. Three checks were run:

1. **Well access (analytic).** Corning 7007 U-bottom: rim Ø6.86 mm, depth 11.30 mm (S13). Capillary OD 1.0 mm, tip 0.3 mm above the well bottom.
2. **Clearance sweep (OpenCascade minimum distance).** All 96 wells at pick height and at safe-Z (plate top + 5 mm), plus a 35-point grid over the full 150 × 100 travel at safe-Z and at the top of the Z stroke. Moving parts are checked against the IX73 envelope, the condensers, the plate and the pump.
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
- **8°** keeps a {{RIM_8:.2f}} mm rim margin and moves the holder about 4 mm off the axis. That leaves annular illumination at NA 0.3, so the tip stays visible while landing. The Zhao et al. 45° mount (S23) is correct for open droplets but not for wells.

The illumination figures are an obstruction estimate, not an optical simulation. **Test M18** (a Ø10 rod at 30–45 mm above focus, 4× and 10×) decides whether 8° is enough or whether 10–12° is needed.

## Condenser constraint

Condenser fronts are placed at well bottom + WD, with WD from manufacturer data (S03, S04). Condenser diameter and body are **placeholders** (Ø80), so all numbers below move once M6–M8 are measured.

| Condenser | WD (MFR) | front above plate top | Result with dog-leg arm (12 mm thick) |
|---|---|---|---|
| IX2-LWUCD | 27 mm | ≈15.7 mm | arm collides at pick height near the axis: **unusable** |
| IX2-MLWCD | 45 mm | ≈33.7 mm | arm collides at pick height near the axis: **unusable** |
| **IX-ULWCD** | 73 mm | ≈61.7 mm | W-A {{SW_WA_R08_ULWCD_PICK}}/96, W-B {{SW_WB_R08_ULWCD_PICK}}/96 at pick height; minimum clearance {{SW_WA_R08_ULWCD_SAFE_CLEAR}} mm at safe-Z (tubing on the arm vs condenser front) |
| none (column tilted back) | – | – | no constraint; needs alternative illumination during picking |

## Collision and interference notes

1. **Condenser.** This is the dominant hazard. With the IX-ULWCD, the Z stroke **above safe-Z is blocked under the condenser** (W-A: {{SW_WA_R08_ULWCD_GRID_TOP}} of 35 grid points at top-Z are clear; W-B: {{SW_WB_R08_ULWCD_GRID_TOP}} of 35). The controller therefore needs a software keep-out zone: a cylinder of radius R_cond + 10 mm around the optical axis in which the tip is not allowed above z = safe-Z. Capillary changes happen at the park position (W-A: X +{{WA_X_MAX}}, Y +{{WA_Y_MAX}}; W-B: X +{{WB_X_MAX}}; Z top), which lies outside the keep-out.
2. **Arm length.** The thin section of the arm must extend from the tip by |tip x min| + condenser radius + margin: {{WA_THIN_L}} mm in W-A, {{WB_THIN_L}} mm in W-B (computed in `params.layout`). An earlier 60 mm thin section collided at safe-Z in columns 1–3; the sweep caught this and the model was corrected. The tall Z actuator stays outboard of the condenser in every position.
3. **Tubing on the arm.** It is the closest item to the condenser ({{SW_WA_R08_ULWCD_SAFE_CLEAR}} mm). Route it along the side of the arm, not on top.
4. **Well walls.** They are the binding constraint on angle (above). The OCC sweep and the analytic check agree: 30° and 45° give {{SW_WA_V30_ULWCD_PICK}}/96.
5. **Plate lid.** The model assumes no lid. A lid adds about 3–4 mm (Corning 7007 is 0.650 in = 16.5 mm high with lid). Lid removal belongs in the workflow.
6. **Stage and plate holder clips.** These are unknown (M11). The arm underside is ≈41 mm above the stage at pick height and ≈57 mm at safe-Z, so it is not critical.
7. **Objective and turret.** They lie below the stage; the picker cannot reach them because nothing moves below z = 0. The risk is to the plate bottom, not the objective: a tip driven through a thin plate bottom would load the plate. Limit this with a firmware Z floor at well bottom − 0.5 mm per plate type, plus a break-away mount.
8. **Microscope frame.** The closest fixed IX73 item to the frame is the body side at x = +161.5 mm. The tower axis is at +{{WA_TOWER_X}} mm in W-A ({{WA_GAP:.0f}} mm gap) and +{{WB_TOWER_X}} mm in W-B ({{WB_GAP:.0f}} mm gap). The X support beam passes over the stage at z ≥ 180 mm; the condenser carrier arm is at x = ±45 mm (placeholder), and the X actuator's inner end is at x = {{WA_X_LO}} mm ({{WA_X_INNER_CLEAR}} mm beyond the condenser radius). **This gap is a placeholder result and must be re-checked after M7.**
9. **Eyepieces / observation tube.** The frame does not use the operator side. A front bridge was rejected because it would sit in the (unknown, M12) eyepiece envelope and in the operator's hand space.
10. **Collision fuse.** The holder arm hangs on a magnet-preloaded 3-ball kinematic mount. A crash detaches the arm instead of bending the capillary or loading the plate, and re-seating is repeatable to a few µm (typical of kinematic mounts; to be verified). Tip re-calibration by image after any detach is still required.
