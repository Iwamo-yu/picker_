# Plate formats and exchangeable angle blocks

![formats](img/formats_angle_blocks.png)

## Conclusion

A single fixed capillary angle serves the 96-well plate well but not the larger wells. The holder therefore takes **exchangeable angle blocks ({{ANGLE_BLOCKS_TXT}})**. The block sits in the **holder seat at the tip end of the arm**, not at the kinematic mount on the Z carriage, so it tilts only the holder and capillary. For each plate format and capillary class, the collet's depth stop sets the **exposed capillary length**. Each block is a fixed, pre-designed geometry, which is more repeatable than a continuous tilt. A block change only needs a 3-point image re-calibration and that plate's soft limits.

## Recommended setting per plate format and capillary class

Computed by `analysis.format_angle_matrix()`. A setting is accepted when all of the following hold:

- rim clearance ≥ {{RIM_MARGIN}} mm (well geometry is manufacturer data);
- holder over plate material ≥ {{MIN_MARGIN:.0f}} mm;
- head top (arm plus tubing allowance) under the condenser front, with the tip at safe-Z, ≥ {{MIN_MARGIN:.0f}} mm (the condenser is still a placeholder);
- for flat-bottom wells, the tip can reach ≥ 50 % of the bottom area.

Among the settings that pass, the one that blocks the least transmitted light (holder plus arm, ray test at NA 0.3) is chosen. Ties go to the larger reachable area, then the longer exposed length.

{{FMT_TABLE_MD}}

Full matrix: `generated_analysis_tables.md` §1c.

## What the matrix shows

1. **Well depth, not diameter, drives the condenser margin.** The 48/24/12/6-well plates are about 17.4 mm deep, against 11.3 mm for the 96-well. Retracting to safe-Z (rim + 5 mm) therefore lifts the head about 6 mm higher under the condenser. A shorter exposed length or a steeper block restores the margin.
2. **Holder stack length is the most sensitive dimension.** Every recommended setting keeps at least {{MIN_MARGIN:.0f}} mm under the condenser only if the holder stack above the collet nose is no longer than about **{{HOLDER_L_MAX_MIN:.1f}} mm**. The model uses {{HOLDER_L:.0f}} mm; an ER8-collet holder with nut, depth stop and seal is likely 20–25 mm (P10, unverified). The holder stack length is therefore a **freeze-gate item**. Mitigations:
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
- Condenser clearance uses the placeholder condenser geometry and must be recomputed after M6 and M8. It also depends one-for-one on the holder stack length (see 2).
