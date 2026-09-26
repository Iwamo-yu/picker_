# Plate formats and exchangeable angle blocks

![formats](img/formats_angle_blocks.png)

## Conclusion

**Scope.** Only the **{{V1_PLATE_SKU}}** 96-well U-bottom plate with the {{V1_THETA:.0f}}° block is V1. The 8° head is designed for that SKU: other 96-well plates have different rim diameters and depths and must be re-checked before use. Everything else on this page ({{EXPERIMENTAL_PLATES}}) is **experimental**: kept in the model to show that the frame can grow, but not part of V1 acceptance or ordering. Plate heights of the experimental plates are not confirmed (`MULTIWELL_HEIGHT_EXTRA`, placeholder).

A single fixed capillary angle serves the 96-well plate well but not the larger wells. The holder therefore takes **exchangeable angle blocks ({{ANGLE_BLOCKS_TXT}})**. The block sits in the **holder seat at the tip end of the arm**, not at the kinematic mount on the Z carriage, so it tilts only the holder and capillary. For each plate format and capillary class, the collet's depth stop sets the **exposed capillary length**. Each block is a fixed, pre-designed geometry, which is more repeatable than a continuous tilt. A block change only needs a 3-point image re-calibration and that plate's soft limits.

## Recommended setting per plate format and capillary class

Computed by `analysis.format_angle_matrix()`. A setting is accepted when all of the following hold:

- rim clearance ≥ {{RIM_MARGIN}} mm (well geometry is manufacturer data);
- holder over plate material ≥ {{MIN_MARGIN:.0f}} mm;
- a positive safe-Z corridor: the head top (arm plus tubing) stays ≥ {{MIN_MARGIN:.0f}} mm under the condenser front with the tip at that plate's corridor lower bound (the condenser is still a placeholder);
- for flat-bottom wells, the tip can reach ≥ 50 % of the bottom area.

Among the settings that pass, the one that blocks the least transmitted light (holder plus arm, ray test at NA 0.3) is chosen. Ties go to the larger reachable area, then the longer exposed length.

{{FMT_TABLE_MD}}

Full matrix: `generated_analysis_tables.md` §1c.

## What the matrix shows

1. **Well depth, not diameter, drives the condenser margin.** The 48/24/12/6-well plates are about 17.4 mm deep, against 11.3 mm for the 96-well. Retracting to safe-Z (rim + 5 mm) therefore lifts the head about 6 mm higher under the condenser. A shorter exposed length or a steeper block restores the margin.
2. **Head height above the nose is the most sensitive dimension.** It is defined once, as the vertical distance from the collet nose to the highest point of the head (holder, arm and tubing), and measured as M23 (`HEAD_TOP_FROM_NOSE_MEAS`). The model uses {{NOSE_TOP_V1:.1f}} mm for the V1 head (holder axial length {{HOLDER_AXIAL_LEN:.0f}} mm, APX). Every recommended setting keeps at least {{MIN_MARGIN:.0f}} mm under the condenser only if this height is no more than about **{{NOSE_TOP_MAX_MIN:.1f}} mm**. An ER8-collet holder with nut, depth stop and seal is likely 20–25 mm long (P10, unverified), so M23 is a **freeze-gate item**. The exported CAD heads are checked against the same formula (`generated_analysis_tables.md` §5d). Mitigations:
   - shorter exposed length (24 mm);
   - a holder that passes *through* the arm, so its top is the head top;
   - the tilted-back illumination option.
3. **Steeper blocks trade light for reach.** At 30° the head casts no shadow at NA 0.3, but a tilted shaft cannot follow objects near the far (+X) wall. That is why the reachable bottom area is an acceptance criterion.
4. **Stand-off must account for the tilted tip.** For a square-cut tip, the lowest edge lies r·sin θ below the tip axis. The tip-axis height tz is therefore raised so that the edge stays ≥ 0.1 mm above the bottom: 0.47 mm for OD 1.5 at 30°, 0.60 mm for OD 2.0. The firmware Z floor must be set per plate × block × capillary class from the *measured* bottom height, never below it.
5. **Some combinations fall short.** The 48-well with OD 1.5/2.0 reaches under 50 % of the bottom at 8°. A 0° block would reach more but blocks most of the light. That choice is left open as D8.
6. **45° is not needed.** In the 6-well the shaft almost touches the rim and the holder nose runs about 0.6 mm above the plate material. In smaller wells the rim blocks it outright.

## Mechanical design intent for the blocks

- The block sits between the arm tip and the holder seat, with two dowels and one clamp screw. Each block carries an engraved angle.
- Changing the block moves the tip relative to the arm by several mm: 44·(cos 8° − cos 30°) ≈ 5.5 mm in height, plus the change in exposed length. Soft limits, the Z floor and the image calibration are therefore stored **per plate × block × capillary class**.
- W-B only: the dog-leg arm and all other parts are unchanged, and the Y/X travel does not depend on the angle.

## Data status

- Plate dimensions are Corning dimension-sheet values read from search excerpts (S13, S16). The 6-well gives a single diameter (34.8 mm), and the 24-well pitch (19.3 mm) is only weakly confirmed.
- Condenser clearance uses the placeholder condenser geometry and must be recomputed after M6 and M8. It also depends one-for-one on the head height above the nose (M23, see 2).
