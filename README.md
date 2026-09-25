# picker_: external XYZ capillary picker for an Evident/Olympus IX73

Stage 1 is a **spatial and mechanical feasibility study**: architecture, placement, travel, actuator stacking, capillary approach, interference with the microscope, and 96-well compatibility. There is no control software and there are no manufacturing drawings yet.

![isometric](docs/img/view_iso.png)

## Answer to the main question

> *What is the cleanest mechanically robust way to place an external XYZ capillary picker around an IX73 so that it reliably reaches all wells of a standard 96-well plate without interfering with the microscope?*

**A side tower bolted to the optical table on the right of the IX73.** A fixed, twice-supported Y beam (100 mm stroke) carries a cantilevered X stage (150 mm), which carries a Z stage (50 mm, 1 mm-lead ball screw). The Z carriage holds a **thin dog-leg arm that reaches under the condenser to a near-vertical (8°) glass capillary**. Nothing touches the microscope. The whole frame unbolts without affecting IX73 alignment.

The layout follows from two constraints found and quantified in this study:

1. **The 96-well limits the angle.** A 1.0 mm capillary reaches the bottom centre of a Corning 7007 U-bottom well (rim Ø6.86 mm, depth 11.30 mm) only within **14.8° of vertical**. At 30° it stops 4.9 mm below the rim; at 45°, 2.7 mm. So 30° and 45° reach **0/96 wells**, whatever the condenser.
2. **A near-vertical capillary must share the optical axis with the condenser.** That fits only under a long-working-distance condenser (**IX-ULWCD, WD 73 mm → 96/96 wells** at pick height and at safe-Z) or with the illumination column tilted back. The IX2-LWUCD (WD 27 mm) and IX2-MLWCD (WD 45 mm) block most positions for every angle.

Two conditions come attached. The condenser outline, the stage height and the eyepiece envelope are **placeholders**, because the IX73 drawing could not be obtained, so clearances near the condenser (4.8–5 mm) must be re-checked after the measurements in `docs/05_measurement_checklist.md`. The workflow choice between locked-stage and moving-stage operation (D1) must also be made before part numbers are frozen.

## Deliverables

| # | Required output | File |
|---|---|---|
| 1 | Editable parametric CAD source | `cad/params.py` (all dimensions with provenance), `cad/model.py` (build123d/OpenCascade) |
| 2 | STEP assembly | `cad/out/assembly_R08_IX-ULWCD.step` (recommended); `assembly_V00/V30/V45_*.step` (comparison); `cad/out/zones_IX-ULWCD.step` (travel, safe-Z, keep-out, light cone) |
| 3 | Visual CAD preview | `viewer/ix73_picker_viewer.html`, interactive and self-contained (pick a well, angle, condenser; colour by data confidence) |
| 4–7 | Isometric / top / side / front views | 3D renders in `docs/img/view_{iso,top,front,side,head}.png`; dimensioned views in `docs/img/dim_{top,front,side}.png/.svg` |
| 8 | Travel-envelope visualisation | `docs/img/dim_top.png` (tip XY travel over all 96 wells), zones in the viewer and STEP |
| 9 | Collision / interference notes | `docs/02_approach_angle_study.md` §Collision notes; `docs/generated_analysis_tables.md` |
| 10 | 0° / 30° / 45° (+8°) comparison | `docs/02_approach_angle_study.md`, `docs/img/approach_angles.png` |
| 11 | Actuator architecture comparison | `docs/04_actuator_comparison.md` |
| 12 | Recommended overall architecture | `docs/03_architecture.md` |
| 13 | Missing IX73 measurements | `docs/05_measurement_checklist.md` |
| 14 | Source manifest | `docs/source_manifest.md`, `references/fetch_references.sh` |
| 15 | Electrical block diagram | `docs/06_electrical.md`, `docs/img/electrical_block_diagram.png` |
| 16 | Assumptions | `docs/07_assumptions_and_open_items.md` |
| 17 | Items NOT to finalise yet | `docs/07_assumptions_and_open_items.md` |
| – | Literature review (5 papers) | `docs/01_literature_review.md` |
| – | Functional diagram (pump → tubing → capillary; PC → XYZ) | `docs/img/functional_diagram.png` |

## Data confidence

Every dimension in `cad/params.py` carries a status. The viewer's DATA CONFIDENCE mode and the dimensioned drawings use the same colour code:

- **STD / MFR** (green): ANSI/SLAS standards, Evident / Corning / THK / MISUMI / Oriental data.
- **DER / DES** (blue): derived or chosen in this study.
- **APX** (amber): catalogue-class envelope, not a frozen part.
- **PH** (red, hatched): placeholder. Must be measured on the real IX73.

The network policy of the authoring session blocked Zenodo, the publishers, Evident, SLAS and the component vendors. Their values come from search-result excerpts, cross-checked where possible, and are marked as such in the manifest. The two SpheroidPicker GitHub repositories were downloaded and read.

## Rebuild

```bash
pip install build123d matplotlib
python cad/model.py        # STEP + STL + parts.json          (~10 s)
python cad/analysis.py     # well access, light obstruction, 96-well clearance sweep (~4 min)
python cad/views.py        # dimensioned views + diagrams
python viewer/build_viewer.py
```

Change any value in `cad/params.py` (for example, replace a `PH` with a measured value) and rerun. Every figure and table is regenerated.
