<!-- GENERATED from docs/src/02_approach_angle_study.md by cad/render_docs.py - edit the source, not this file -->
# Capillary approach: 0° vs 8° vs 30° vs 45°, plus collision and interference notes

Figures: `img/approach_angles.png`, `img/view_head.png`, `img/dim_front.png`. The raw numbers are in `generated_analysis_tables.md`, produced by `cad/analysis.py`.

## Conclusion

The capillary's last segment must be **near-vertical (0–12°)**. The binding constraint is the 96-well itself, not the condenser. A near-vertical capillary then has to share the space on the optical axis with the condenser. That works only if (a) the condenser has a long working distance (IX-ULWCD, WD 73 mm) and the picker reaches in with a thin horizontal "dog-leg" arm below it, or (b) the illumination column is tilted back during picking. With the IX2-LWUCD (WD 27 mm) no angle works. **8° with a dog-leg arm** is the recommended geometry for 96-well plates. The angle is set by exchangeable angle blocks (8° / 20° / 30°), one per plate format (`10_plate_formats_angle_blocks.md`), not by a continuous tilt.

## Method

Every angle uses the same external frame and the same outboard Z position, with the W-A frame (180 mm arm, picker covering the plate; the W-B frame gives the same angle results at the optical axis). Only the capillary/holder angle changes, so the comparison isolates the effect of angle. Three checks were run:

1. **Well access (analytic).** Corning 7007 U-bottom: rim Ø6.86 mm, depth 11.30 mm (S13). Capillary OD 1.0 mm, tip 0.3 mm above the well bottom.
2. **Clearance sweep (OpenCascade minimum distance).** All 96 wells at pick height and at safe-Z (plate top + 5 mm), plus a 35-point grid over the full 150 × 100 travel at safe-Z and at the top of the Z stroke. Moving parts are checked against the IX73 envelope, the condensers, the plate and the pump.
3. **Illumination obstruction (analytic).** Fraction of the condenser light cone blocked by the Ø10 holder at its nose height.

## Results

| Criterion | 0° | **8° (rec.)** | 30° | 45° |
|---|---|---|---|---|
| Rim clearance, tip at well-bottom centre | +2.93 mm | **+1.38 mm** | -3.50 mm (hits rim) | -8.28 mm (hits rim) |
| Deepest centred reach below the rim | full (11.3 mm) | **full** | 4.9 mm | 2.7 mm |
| Wells reachable at pick height, IX-ULWCD | 96/96 | **96/96** | 0/96 | 0/96 |
| Wells reachable at pick height, IX2-LWUCD | 10/96 | 16/96 | 0/96 | 0/96 |
| Wells reachable at pick height, pillar tilted back | 96/96 | **96/96** | 0/96 | 0/96 |
| Illumination blocked by holder, condenser NA 0.1 / 0.3 | 100 % / 28 % | 61 % / 28 % | 0 % / 0 % | 0 % / 0 % |
| Tip visible beside holder in transmitted light | no (coaxial) | partly | yes | yes |
| Cantilever from holder to tip (exposed glass) | 30 mm | 30 mm | 30 mm | 30 mm |
| Lateral tip compliance from tubing/drag forces | lowest | low | medium (bending ∝ sin θ) | highest |
| Tubing exit | vertical, turns into arm | same | along capillary axis, higher | lowest, near plate |
| Maximum angle for bottom-centre access | | 14.8° (no margin) | | |

**Reading the table.**

- **30° and 45° fail** for any standard 96-well plate. The shaft meets the rim long before the tip reaches the bottom. That holds whatever condenser is fitted. An angled capillary also cannot follow an object off-centre on the far side of a U-bottom.
- **0° is geometrically best** for the wells, but the holder sits coaxially above the tip. At low condenser NA it blocks the whole light cone, so transmitted-light imaging during the landing is lost.
- **8°** keeps a 1.38 mm rim margin and moves the holder about 4 mm off the axis. Including the arm, the head still blocks about a third of the NA 0.3 cone at 8° (ray test, `generated_analysis_tables.md` §2), so the image is darker during landing but the tip remains visible beside the holder. The Zhao et al. 45° mount (S23) is correct for open droplets but not for wells.

The illumination figures are an obstruction estimate, not an optical simulation. **Test M18** (a Ø10 rod at 30–45 mm above focus, 4× and 10×) decides whether the 8° block is enough for 96-well work or whether a 10–12° block should be added.

## Condenser constraint

Condenser fronts are placed at well bottom + WD, with WD from manufacturer data (S03, S04). Condenser diameter and body are **placeholders** (Ø80), so all numbers below move once M6–M8 are measured.

| Condenser | WD (MFR) | front above plate top | Result with dog-leg arm (12 mm thick) |
|---|---|---|---|
| IX2-LWUCD | 27 mm | ≈15.7 mm | arm collides at pick height near the axis: **unusable** |
| IX2-MLWCD | 45 mm | ≈33.7 mm | arm collides at pick height near the axis: **unusable** |
| **IX-ULWCD** | 73 mm | ≈61.7 mm | W-A 96/96, W-B 96/96 at pick height; minimum clearance 4.83 mm at safe-Z (tubing on the arm vs condenser front) |
| none (column tilted back) | – | – | no constraint; needs alternative illumination during picking |

## Collision and interference notes

1. **Condenser.** This is the dominant hazard. Under the IX-ULWCD the Z stroke **above the reference height is blocked near the axis**. W-A: 20 of 35 grid points at top-Z are clear; W-B: 15 of 35. In W-A the arm reaches 120 mm towards +X, so collisions also occur with the tip *outside* a simple cylinder around the axis. The control rule is therefore: **Z may go above the reference switch height only at the park position** (X ≥ park), and homing lifts Z to the reference switch first (`06_electrical.md`). Capillary changes happen at park.
2. **Arm length.** The thin section of the arm must extend from the tip by |tip x min| + condenser radius + margin: 120 mm in W-A, 60 mm in W-B (computed in `params.layout`). (During the W-A iteration, a 60 mm thin section collided at safe-Z in columns 1–3. The sweep caught it, and the rule above was derived from it.) The tall Z actuator stays outboard of the condenser in every position.
3. **Tubing on the arm.** It is the closest item to the condenser (4.83 mm). Route it along the side of the arm, not on top.
4. **Well walls.** They are the binding constraint on angle (above). The OCC sweep and the analytic check agree: 30° and 45° give 0/96.
5. **Plate lid.** The model assumes no lid. A lid adds about 2 mm (Corning 7007 is 0.650 in = 16.5 mm high with lid, against 14.35 mm without). Lid removal belongs in the workflow.
6. **Stage and plate holder clips.** These are unknown (M3). The arm underside is ≈41 mm above the stage at pick height and ≈57 mm at safe-Z, so it is not critical.
7. **Objective and turret.** They lie below the stage; the picker cannot reach them because nothing moves below z = 0. The risk is to the plate bottom, not the objective: a tip driven through a thin plate bottom would load the plate. Limit this with a firmware Z floor at the **measured** well bottom + r·sin θ + 0.1 mm per plate × block × capillary class (the lowest edge of a tilted square-cut tip), never below the bottom.
8. **Microscope frame.** The closest fixed IX73 item to the frame is the body side at x = +161.5 mm. The tower axis is at +408 mm in W-A (246 mm gap) and +368 mm in W-B (206 mm gap). The X support beam passes over the stage at z ≥ 180 mm; the condenser carrier arm is at x = ±45 mm (placeholder), and the X actuator's inner end is at x = 60 mm (20 mm beyond the condenser radius). **This gap is a placeholder result and must be re-checked after M7.**
9. **Eyepieces / observation tube.** The frame does not use the operator side. A front bridge was rejected because it would sit in the (unknown, M12) eyepiece envelope and in the operator's hand space.
10. **Collision fuse.** The arm hangs on a magnet-preloaded kinematic mount (e.g. Thorlabs KB25/M, about 16 N holding force, P12). Its release force at the 115 mm arm lever is about 1–2 N. That protects the plate, stage and condenser from a stalled axis, but **not the capillary**: a 1.0 mm glass capillary on a 30 mm cantilever breaks at roughly 0.15 N lateral load (estimate). Treat capillaries as consumables in a crash. Size the release force explicitly when the holder is designed, and re-calibrate after any detach.
