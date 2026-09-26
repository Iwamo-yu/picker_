<!-- GENERATED from docs/src/01_literature_review.md by cad/render_docs.py - edit the source, not this file -->
# Literature review: engineering principles for the IX73 picker

**Scope and limitation.** Full texts were not reachable from this session (nature.com, biorxiv, PMC and ScienceDirect were all denied; see `source_manifest.md`). Each summary below rests on the abstracts and search-result excerpts of the publisher pages. For SpheroidPicker it also rests on the public control software, which was downloaded and read (S28). Statements that need the full text are marked **[verify in full text]**. The review is limited to what changes a mechanical decision.

## 1. Grexa et al. 2021, SpheroidPicker (*Sci. Rep.*) [S20, S27, S28]

**Mechanical architecture.** A two-axis micromanipulator sits next to a Leica stereo microscope (S9i with a Tango Mini motorised XY stage, per `ahmconfig.xml`). It is built from OpenBuilds actuators: a 2080 C-beam frame, four-wheel V-wheel carriages, and an M8 threaded rod (2 mm pitch) driven directly by a NEMA17. The two actuators are assembled at 90°: one gives axial positioning, the other sets the pipette height. The syringe pump is custom, stepper-driven and 3D-printed. Plate holders are 3D-printed for 24/96/384-well plates.

**Positioning strategy.** The microscope's motorised stage brings the object under the optics. The manipulator only brings the capillary to the image position. The software converts image coordinates to pipette coordinates with a 3-point calibration (`controller::pipette_calc_TM`: three saved pipette positions against three fixed image points). The pick sequence (`auto_methods::pickup_sph`) is: move to the image coordinate, wait 7 s, apply a vacuum pulse, wait 3 s, then **home Z** (retreat upward to the homing switch).

**Capillary.** A glass capillary rod sits in a capillary holder fixed to a 3D-printed part. OD, ID and angle need the full text or the Zenodo STL files **[verify in full text / S25]**. The user-given reference (OD 1.0 / ID 0.6 / L 40) is used here.

**Fluidics.** The custom syringe pump is run as the firmware's extruder axis (`pipette_extrude_relative`, "E" G-code). Resolution is quoted as 3 µl.

**Microscope integration.** A stereo microscope observes from above, so the capillary shares the space above the sample with the objective, not with a condenser. The IX73 case is harder: the condenser occupies the space above the sample on the optical axis.

**Useful principles.** (i) Let one stage own coarse XY and let the picker work near the optical axis. (ii) Calibrate the tip in image coordinates rather than trusting mechanical absolute accuracy. (iii) Retreat by homing Z after every pick. That makes the safe-Z a switch-defined physical position.

**Limitation for IX73.** C-beam/V-wheel carriages and threaded rod have backlash and preload drift. The 2-axis manipulator relies on a motorised microscope stage. The stereo-microscope geometry does not transfer to an inverted microscope with a condenser.

**Decision.** *Copy*: image-space 3-point calibration, pick sequence with dwell and Z-home retreat, G-code-type controller with pump as a separate channel. *Modify*: replace C-beam/V-wheel/M8 rod with ball-screw stages; add a third axis because the IX73 stage is not assumed motorised. *Ignore*: the custom syringe pump (the lab pumps are used).

## 2. Diosdi et al. 2025, HCS-3DX (*Nat. Commun.*) [S21, S26]

**Architecture.** HCS-3DX has three parts: an AI-driven micromanipulator (SpheroidPicker) for 3D-oid selection and transfer, an FEP-foil multiwell plate for light-sheet imaging, and AI analysis software. The picker hardware is the SpheroidPicker lineage. The public GitHub/Zenodo release (tag `HCS-3DX`, S27) contains the software, and the 3D-printed parts are on Zenodo 14679243 (not retrievable here).

**Useful principle.** The picker is a pre-selection and transfer tool for a downstream imaging plate. That favours reliable, repeatable transfer between *standard SBS plates* over high speed. It supports a design with a slow, well-defined Z approach.

**Limitation.** No new mechanical data were available beyond SpheroidPicker **[verify in full text: any changes in capillary diameter or holder]**.

**Decision.** *Copy* the workflow framing (select → transfer → verify). *Ignore* the LSFM plate for this design stage.

## 3. Környei et al. 2013, CellSorter (*Sci. Rep.*) [S22]

**Architecture.** A pulled glass micropipette (50 µm opening) sits on a motorised micromanipulator (Märzhäuser SM 3.25). A pressure controller acts through a fast normally-closed liquid valve between the pipette and a syringe pump. It is installed on an inverted microscope (Nikon Eclipse Ti) with a motorised stage and 10×/20×/40× objectives.

**Positioning strategy.** The motorised stage brings cells under the pipette. The pipette tip is held **30 µm above the dish surface** during operation. Sorting resolution is 50–70 µm between cells.

**Fluidics.** A syringe pump plus a fast valve gives short, defined suction pulses. The liquid-filled line is hydraulically stiff.

**Useful principles.** (i) A fixed, small tip-to-bottom stand-off is taught once and reused. For 100–500 µm spheroids in U-bottom wells the equivalent stand-off is roughly 100–300 µm, set against the well bottom found by a slow touch-down. (ii) A valve between pump and pipette decouples pump dynamics from the pick pulse. (iii) Imaging on an inverted microscope is not blocked by a thin pipette.

**Limitation for IX73.** Tiny volumes (single cells) and a flat Petri dish mean the pipette angle is unconstrained by walls. Here, 96-well walls dominate.

**Decision.** *Copy* the fixed stand-off concept and an optional pinch/NC valve near the holder (keep it on the fixed frame, not on the head). *Modify* the scale (spheroid volumes). *Ignore* the single-cell hydrodynamics.

## 4. Zhao et al. 2026, micropipette-resistance-based cell transport (*Microsyst. Nanoeng.*) [S23]

**Architecture.** A robotic system transports cells between droplets without microscope guidance. A narrow-necked micropipette holds the cell. Gap, aspiration and injection resistance models are used to land on the dish and to confirm pick and place. Each micropipette is **mounted at 45°**, and the tip moves down to contact the dish bottom **at 10 µm/s**.

**Useful principles.** (i) A slow, constant-speed final approach (≈10 µm/s over the last ~100 µm) lets you detect contact. (ii) Pickup and release can be confirmed by a non-optical signal, such as a pressure or resistance change in the line.

**Limitation for IX73.** The 45° mount works because droplets and Petri dishes have no walls. In a 96-well plate a 45° capillary reaches only 2.7 mm below the rim (see `02_approach_angle_study.md`). Resistance sensing needs electrolyte continuity and electrodes, which is not needed for a first prototype.

**Decision.** *Copy* the constant-speed slow landing and keep a pressure port or transducer tee on the fixed part of the fluid line for later pick confirmation. *Ignore* the 45° angle for 96-well work. *Defer* resistance sensing.

## 5. Kovacs … Horvath 2025, NanoPick large-volume piezo micropipette (*Colloids Surf. B*) [S24]

Note: the first author is Kovacs B.; Horvath R. is the senior author.

**Architecture.** A piezoelectric micropipette head (NanoPick, 0.1–600 nl, 1 ms resolution) sits on a **1-D micromanipulator** attached to an inverted microscope. The head is built above the objective, and the motorised microscope stage aligns the sample between them. No fluid tubes or syringes are used; the piezo displaces the volume inside the head. Imaging (phase contrast and fluorescence) is not limited by the pipette.

**Useful principles.** (i) Minimal axes: XY from the microscope stage, Z only for the pipette. That is the most compact and stiffest option when a motorised stage exists. (ii) Putting the volume actuator in the head removes tubing compliance and tubing drag.

**Limitation for IX73.** It requires a motorised stage (unknown for our IX73; the manual IX3-SVR is assumed). The volume range (≤600 nl) is too small for spheroid transfer, which needs microlitres. A head-mounted actuator adds moving mass.

**Decision.** *Keep as an alternative architecture* (motorised IX73 stage + Z-only picker; see `03_architecture.md` §8). *Ignore* the piezo volume head for spheroids.

## Cross-paper conclusions used in the CAD

| Principle | Source | Where it appears |
|---|---|---|
| Calibrate the tip in image coordinates (≥3 points); do not rely on absolute mechanical accuracy | S20/S28 | holder does not need µm-reproducible tip position; re-calibrate after capillary change |
| Z retreat by homing to a switch after every pick | S28 | Z home switch at the top; safe-Z = plate top + 5 mm |
| Fixed tip stand-off above the bottom, found by slow touch-down | S22, S23 | `TIP_CLEAR_BOTTOM` = 0.3 mm in the model; landing speed ≈10 µm/s |
| Inclined pipettes are normal in open dishes but not in deep wells | S23 vs. 96-well geometry | near-vertical 8° head |
| Minimal axes when a motorised stage exists | S24, S22 | alternative architecture in §8 of `03_architecture.md` |
| Keep valve, pressure tee and pump off the moving head | S22, S28 | fixed clamp on the frame, pump off-frame |
