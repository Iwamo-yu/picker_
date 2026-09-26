# Capillary sizing for 100 µm – 1 mm objects

Requirement (2026-09-26): objects from **about 100 µm to 1 mm** must be pickable.

## Conclusion

A single capillary cannot cover a 10:1 size range well, so the holder takes **interchangeable capillaries in three OD classes (1.0 / 1.5 / 2.0 mm)**. The 8° approach and the frame stay unchanged: even the 2.0 mm OD capillary keeps 0.87 mm rim clearance in a Corning 7007 well at 8°. The OD therefore changes only the collet insert, not the geometry.

## Proposed set

The ratio rule below is 【私の提案 / proposal】, not taken from a source. It targets **ID ≈ 1.3–3 × object diameter**. The lower bound is set so the object enters the bore without being squeezed. The upper bound limits how much surrounding liquid (and neighbouring debris) is taken up. Both ends must be confirmed by pick tests with real objects.

| Class | Object | Capillary (OD / ID, mm) | ID ÷ object | Max angle for bottom centre | Rim clearance at 8° | Data |
|---|---|---|---|---|---|---|
| S | 100–300 µm | 1.0 / 0.58 (WPI 1B100-4) | 1.9–5.8 | 14.8° | 1.38 mm | MFR (S14) |
| S′ | ~100 µm, when selectivity matters | 1.0 OD, tip cut or pulled to ID 0.2–0.35 | 2–3.5 | 14.8° | 1.38 mm | shaft MFR; tip made in-house |
| M | 300–600 µm | 1.5 / 0.84 (WPI 1B150-4; Sutter B150-86 = 0.86) | 1.4–2.8 | 13.6° | 1.13 mm | MFR (S14) |
| L | 600–1000 µm | 2.0 / 1.12 (WPI 1B200-4) | 1.1–1.9 | 12.3° | 0.87 mm | MFR (S14) |
| L′ | 800–1000 µm | 2.0 OD thin wall, ID ≈ 1.5 | 1.5–1.9 | 12.3° | 0.87 mm | **PH**: ID not verified |

Notes:

- **1 mm objects.** A standard-wall 2.0 mm capillary (ID 1.12) is only 1.12 × a 1 mm object, which is marginal. A thin-wall 2.0 mm tube is preferred, but its ID was not verified in this session.
- **100 µm objects.** The 1.0/0.58 capillary picks them easily but draws about 30 × the object's cross-section. Where one object per U-bottom well is typical, that is acceptable. When selectivity or a small volume matters, use class S′: the same 1.0 mm shaft, so no holder change.
- **Volume per pick.** Drawing a 2 mm plug into the bore takes about 0.5 µL (S), 1.1 µL (M) or 2.0 µL (L, ID 1.12). That is within the working range of a syringe pump with a small syringe. Pick the syringe size for resolution (for example 25–100 µL) together with the pump model (M17).

## Effect on the mechanics

- **Well access.** The maximum angle falls from 14.8° (OD 1.0) to 12.3° (OD 2.0). The recommended 8° fixed angle is kept for all classes.
- **Holder.** A collet with **exchangeable inserts for OD 1.0 / 1.5 / 2.0** fits in the same Ø10 mm envelope. The depth stop and liquid-port seal are per insert. If a Ø12 mm body turns out to be needed for the 2.0 mm insert, holder obstruction of the light cone rises slightly; re-run `analysis.py` with `HOLDER_D = 12`.
- **Tubing.** 1/16″ OD tubing connects to all classes through the holder port, so tubing needs no change.
- **Calibration.** After changing class, re-run the 3-point image calibration (tip position changes by up to ±0.5 mm between classes).

## Still to confirm

- Object size distribution in real samples (spheroids, particles, hydrogel beads), and whether soft objects tolerate ID ≈ 1.1–1.3 × diameter.
- Thin-wall 2.0 mm capillary ID (catalogue check).
- Pick tests per class: success rate, carry-over volume, damage.
