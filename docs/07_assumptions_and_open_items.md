# Assumptions, open decisions and items NOT to finalise yet

## Assumptions made in this iteration

1. Coordinate frame: origin at the optical axis on the stage-insert top; the plate is centred on the axis at the "reference stage position" with A1 at rear-left.
2. Stage top is 200 mm above the table. **Placeholder** (M1). The frame height scales with it.
3. The IX73 body is centred on the optical axis in X. The body front face is at y = −235 mm. The pillar and condenser arm are ±45 mm wide. The condenser is Ø80 × 70 mm. **All placeholders** (M5–M9).
4. Condenser working distances are the manufacturer values (27/45/73 mm), measured from the well-bottom plane. The real front-lens height at the focus used may differ by a few mm (M8).
5. The plate is Corning 7007 geometry (U-bottom ULA, rim Ø6.86, depth 11.30), with no lid during picking.
6. Capillary: OD 1.0 / ID 0.6 / L 40, gripped 10 mm, 30 mm exposed. Tip stand-off 0.3 mm above the well bottom (model value; the process value is set experimentally).
7. The IX73 stage is the manual IX3-SVR (not motorised). It is not loaded by the picker and is locked during automatic runs.
8. The table has free space to the right of the microscope to about +500 mm from the optical axis (+760 mm including the pump and controller).
9. Actuator envelopes are width-26 class ball-screw stages; masses are ±30 % estimates.
10. Deflections are hand estimates (aluminium, simple beams); no FEA.
11. The pump, tubing and fluid volumes do not constrain the mechanics beyond a 1/16" tubing path with ≥25 mm bend radius.

## Open decisions (owner: user)

| ID | Decision | Options | Effect |
|---|---|---|---|
| D1 | Workflow frame | (a) stage locked, blind dispense; (b) stage moves source wells over objective | travel, whether a motorised stage is needed |
| D2 | Condenser during picking | IX-ULWCD (buy or borrow if not present) vs tilt column back + LED ring | whether the dog-leg arm is needed |
| D3 | Final capillary lean | 0–12°, after test M18 | holder seat angle |
| D4 | Side of tower | right (default) vs left (mirror) | after M12/M13/M15 |
| D6 | Capillary classes to stock | S/M/L (OD 1.0/1.5/2.0) vs fewer; thin-wall 2.0 for 1 mm objects | collet inserts, syringe size |
| D5 | Z actuator type | open-loop ball screw vs closed-loop absolute (DRS2) with brake | cost, homing strategy |

## Items that should NOT be finalised yet

- Actuator part numbers, strokes rounded to catalogue steps, motor frame lengths.
- Bracket geometry, fasteners, dowel positions, machining tolerances and drawings.
- Frame section sizes (80 × 80 posts/beam, 40 × 80 X support) beyond the envelope level. They need the real height (M1) and a stiffness check.
- Dog-leg arm length (175 mm) and thickness (12 mm). Both depend on the condenser diameter and height (M6–M8).
- Holder design (collet size, port type, kinematic mount).
- Base-plate hole pattern (M16).
- Tubing type, bore and length (pump choice M17, dead volume).
- Cable chain sizes, connector types, controller board, PSU rating.
- Safe-Z value, keep-out zone radius and approach speeds (process tests).
- Any change to the IX73 (none planned).
