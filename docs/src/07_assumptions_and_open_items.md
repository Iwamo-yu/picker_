# Assumptions, open decisions and items NOT to finalise yet

## Assumptions made in this iteration

1. Coordinate frame: origin at the optical axis on the stage-insert top; the plate is centred on the axis at the "reference stage position" with A1 at rear-left.
2. Stage top is 200 mm above the table. **Placeholder** (M1). The frame height scales with it.
3. The IX73 body is centred on the optical axis in X. The body front face is at y = −235 mm. The pillar and condenser arm are ±45 mm wide. The condenser is Ø80 × 70 mm. **All placeholders** (M5–M9).
4. Condenser working distances are the manufacturer values (27/45/73 mm), measured from the well-bottom plane. The real front-lens height at the focus used may differ by a few mm (M8).
5. The plate is Corning 7007 geometry (U-bottom ULA, rim Ø6.86, depth 11.30), with no lid during picking.
6. Capillary: OD 1.0 / ID 0.6 / L 40, gripped 10 mm, 30 mm exposed. Tip stand-off 0.3 mm above the well bottom (model value; the process value is set experimentally).
7. The IX73 stage is modelled as the manual IX3-SVR (114 × 75 mm). In W-B it is replaced by, or treated as, a motorised stage with ≥ 99 × 63 mm travel that carries only the plate. The picker never loads the stage.
8. The table has free space to the right of the microscope to about +{{WA_FOOT_X}} mm (W-A) / +{{WB_FOOT_X}} mm (W-B) from the optical axis, plus the pump and controller beyond.
9. Actuator envelopes are width-26 class ball-screw stages; masses are ±30 % estimates.
10. Deflections are hand estimates (aluminium, simple beams); no FEA.
11. The pump, tubing and fluid volumes do not constrain the mechanics beyond a 1/16" tubing path with ≥25 mm bend radius.

## Open decisions (owner: user)

| ID | Decision | Options | Effect |
|---|---|---|---|
| D1 | Workflow | **provisional: W-B** (stage moves wells to the axis; all picks observed) vs W-A (stage fixed, blind outside the axis) — `09_workflow_D1.md` | picker travel, motorised stage ≥ 99 × 63 mm (not IX3-SSU) |
| D2 | Condenser during picking | IX-ULWCD (buy or borrow if not present) vs tilt column back + LED ring | whether the dog-leg arm is needed |
| D3 | Angle-block set | {{ANGLE_BLOCKS_TXT}} per plate format; add a 10–12° block only if test M18 requires it | angle blocks, calibration |
| D4 | Side of tower | right (default) vs left (mirror) | after M12/M13/M15 |
| D5 | Z actuator type | open-loop ball screw vs closed-loop absolute (DRS2) with brake | cost, homing strategy |
| D6 | Capillary classes to stock | S/M/L (OD 1.0/1.5/2.0) vs fewer; thin-wall 2.0 for 1 mm objects | collet inserts, syringe size |
| D7 | Motorised stage for W-B | Märzhäuser SCAN IM 120 × 80 class or equivalent (IX3-SSU 76 × 52 is too small) | cost, controller integration |

## Items that should NOT be finalised yet

Freeze gate: nothing below is frozen before M1, M3, M4, M6, M7, M8, M10 and M15 are measured and entered in `cad/params.py`.


- Actuator part numbers, strokes rounded to catalogue steps, motor frame lengths.
- Bracket geometry, fasteners, dowel positions, machining tolerances and drawings.
- Frame section sizes (80 × 80 posts/beam, 40 × 80 X support) beyond the envelope level. They need the real height (M1) and a stiffness check.
- Dog-leg arm length ({{WB_ARM_L}} mm in W-B, {{WA_ARM_L}} mm in W-A) and thickness ({{ARM_T_TXT}}). Both depend on the condenser diameter and height (M6–M8).
- Holder design (collet size, port type, kinematic mount). No commercial holder was found that positively grips OD 1.0/1.5/2.0 with a side port; the lead candidate is a custom body with ER8 collets (P10). Its nut may exceed the Ø10 mm holder envelope used in the analysis (unverified). If so, re-run `analysis.py` with the larger `HOLDER_D`.
- Budget: industrial stages on all three axes are estimated at roughly JPY 250–350k for the picker (parts research, unverified); a cheaper integrated Y stage keeps it near JPY 200k.
- IX-ULWCD availability (P09): one excerpt reports it as not available in some regions. Confirm with Evident Japan first.
- Base-plate hole pattern (M16).
- Tubing type, bore and length (pump choice M17, dead volume).
- Cable chain sizes, connector types, controller board, PSU rating.
- Safe-Z value, keep-out zone radius and approach speeds (process tests).
- Any change to the IX73 (none planned).
