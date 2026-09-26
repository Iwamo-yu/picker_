<!-- GENERATED from docs/src/10_plate_formats_angle_blocks.md by cad/render_docs.py - edit the source, not this file -->
# Plate formats and exchangeable angle blocks

![formats](img/formats_angle_blocks.png)

## Conclusion

A single fixed capillary angle serves the 96-well plate well but wastes the larger wells. The holder therefore sits on **exchangeable angle blocks (8° / 20° / 30°)** that seat on the kinematic mount. The depth stop in the collet sets the **exposed capillary length** for each plate format. Each block is a fixed, pre-designed geometry, which is more repeatable than a continuous tilt. Changing a block only needs a 3-point image re-calibration.

## Recommended setting per plate format

These values are computed by `analysis.format_angle_matrix()`. Acceptance criteria: rim clearance ≥ 0.5 mm (well geometry is manufacturer data); holder-over-plate and condenser clearance at safe-Z ≥ 2 mm (the condenser is still a placeholder). Among the settings that pass, the one with the least shadow in the transmitted-light cone wins.

| Plate | Angle block | Exposed length | Rim clearance | Condenser clearance at safe-Z | Light blocked (NA 0.3) |
|---|---|---|---|---|---|
| 96-well U-bottom (Corning 7007) | 8° | 30 mm | 1.38 mm | 7.1 mm | 28 % |
| 48-well (Corning 3548) | 8° | 27 mm | 2.87 mm | 4.0 mm | 34 % |
| 24-well (Corning 3524) | 20° | 30 mm | 1.37 mm | 3.3 mm | 9 % |
| 12-well (Corning 3513) | 30° | 30 mm | 0.86 mm | 6.4 mm | 0 % |
| 6-well (Corning 3516) | 30° | 30 mm | 6.95 mm | 6.5 mm | 0 % |

The full angle × format matrix is in `generated_analysis_tables.md` §1c.

## What the matrix shows

1. **Well depth, not diameter, drives the condenser margin.** The 48/24/12/6-well plates are about 17.4 mm deep, against 11.3 mm for the 96-well. Retracting to safe-Z (rim + 5 mm) therefore lifts the head about 6 mm higher under the condenser. At 8° with 30 mm exposed, only about 1 mm is left under the IX-ULWCD. A shorter exposed length (27 mm) or a steeper block restores the margin.
2. **Steeper blocks move the holder out of the light cone.** At 30° the holder casts no shadow at NA 0.3. Large wells (12/6-well) allow it, and in those wells the tip also stays visible beside the holder.
3. **45° is not needed.** In the 6-well the shaft almost touches the rim and the holder nose runs about 0.6 mm above the plate material. In smaller wells the rim blocks it outright. A 45° block is therefore not part of the set.
4. **The 12-well at 30° has only 0.86 mm rim clearance**, which is thin for off-centre objects. Keep the 20° block as that plate's fallback.

## Mechanical design intent for the blocks

- The block sits between the kinematic mount and the holder seat, with two dowels and one clamp screw. Each block carries an engraved angle.
- Each block's geometry places the tip at the same nominal point relative to the Z carriage (±1 mm), so the soft limits and keep-out zone stay valid. Exact tip registration still comes from the image calibration.
- W-B only: the dog-leg arm and every other part are unchanged. The Y/X travel does not depend on the angle.

## Data status

- The plate dimensions are Corning dimension-sheet values from search excerpts (S13, S16). The 6-well gives a single diameter (34.8 mm). The 24-well pitch (19.3 mm) is only weakly confirmed.
- Condenser clearance uses the placeholder condenser geometry. It must be recomputed after M6 and M8.
