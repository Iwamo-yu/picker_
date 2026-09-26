# Measurement checklist for the real IX73 (do this before detailed CAD)

Reference frame: origin at the optical axis on the stage-insert top surface; +X operator's right, +Y away from the operator, +Z up. Photograph each measurement with a ruler in view. Enter the values in `cad/params.py`, change their status from `PH` to `MEAS`, and re-run `python tools/build_all.py`.

**Priority:** A = decides feasibility now; B = needed before brackets; C = nice to have.

**Freeze gate:** {{FREEZE_GATE}} must be measured before any bracket or part number is frozen (`09_workflow_D1.md`). For W-B, also record the chosen motorised stage's envelope and travel.

| ID | Pri | Measurement | Currently in model | Why it matters |
|---|---|---|---|---|
| M1 | A | Optical-table surface → stage-insert top (plate resting plane) | 200 mm PH | post/beam height, overall frame |
| M2 | A | Table → top of plate (with the plate type actually used), and plate position on the stage insert (which corner is A1) | derived from SLAS | well coordinates, safe-Z |
| M3 | A | Stage outline (with IX3-SVR fitted), stage-insert opening, clips/holders protruding above the plate top | 232 × 240 MFR plain stage | arm clearance at pick height |
| M4 | A | Stage centre vs optical axis at the "reference position"; lockability of the stage | assumed centred | workflow D1 |
| M5 | B | Distances from optical axis to body front, rear, left, right faces | W/D MFR, position PH | tower placement |
| M6 | A | **Condenser model(s) available in the lab** (IX2-LWUCD? IX-ULWCD? MLWCD?) and outer diameter | Ø80 PH | decides the whole approach (`02_…`) |
| M7 | A | Condenser carrier / arm: width, lowest point, distance from axis to its left/right faces | ±45 mm PH | X support beam clearance (5 mm in model) |
| M8 | A | Condenser front-lens height above plate top with the condenser focused for 4× and 10× (real WD in use) | WD MFR + derived | clearance under the condenser. Enter the measured front height above the stage top as `COND_FRONT_Z_MEAS` in `cad/params.py`. |
| M9 | B | Illumination pillar: position, section, height; lamp housing envelope | PH | rear clearance |
| M10 | A | Illumination column tilted back: angle, and envelope of the column in the tilted position | PH | fallback option |
| M11 | B | Free height above the plate with the condenser raised to its top stop | – | capillary change position |
| M12 | B | Observation tube / eyepieces envelope (front), and any side port and camera on the left/right | PH | confirms no front/side conflict |
| M13 | B | IX3-SVR handle position and swing envelope (right side), focus knob positions both sides | PH | tower and hand access |
| M14 | B | Objective/turret: highest point below the stage at the largest objective used | PH | Z floor safety |
| M15 | A | Free table space to the right: x from the body side to the table edge; y extent; other equipment (incubator, controller, PC) | assumes ≥ +500 mm | frame footprint |
| M16 | B | Optical-table hole pattern (metric M6/25 or imperial ¼-20/1"), hole positions relative to the IX73 feet | – | base plate slots |
| M17 | B | Pump model(s) available, footprint, tubing port, control interface (RS-232/USB) | PH box | placement, fluidic line length |
| M18 | A | **Illumination test**: hold a Ø10 mm rod 30–45 mm above focus, offset 0/4/8 mm from the axis, at 4× and 10×, condenser aperture open and closed; photograph the image | analytic estimate | confirms 8° vs 10–12° choice |
| M19 | C | Plate types to support (U-bottom ULA, flat, spheroid microcavity); their well depth and rim Ø | Corning 7007 | angle margin |
| M20 | C | Vibration: table isolation on/off; bench vs floated table | – | settle time before pick |
| M21 | B | Where the plate lid is placed during work | none | workflow |
| M22 | C | Cable routes to the PC/controller location | – | cable lengths |
| M23 | A | **Holder stack height**: with the real holder (collet, nut, depth stop, seal, side port) mounted on its angle block, the distance from the collet nose to the highest point of the head, including the tubing clip | `HOLDER_L` {{HOLDER_L:.0f}} mm + arm + {{HEAD_TOP_ALLOW}} mm tubing | condenser margin falls about 1 mm per mm; limit ≈ {{HOLDER_L_MAX_MIN:.1f}} mm (`10_…`) |
