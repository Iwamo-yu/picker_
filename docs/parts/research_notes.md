# Stage-1 parts research notes (workflow W-B side-tower picker)

Retrieval date: 2026-09-26. Method: web search only. Vendor pages (MISUMI, THK, Oriental, Evident, Thorlabs, IDEX) could not be opened, so every value below comes from a search-result excerpt of the named page. "Unverified" means that no excerpt showed the value, or only one weak source did. Prices are **approximate**, in the currency found, and several are old or from non-Japanese resellers. Get quotes before ordering. The line items are in `candidates.csv` (P01–P38).

Baseline travels come from `cad/params.py` `layout("WB")`: tip X 100 mm (-15…+85), Y 30 mm, Z 50 mm.

## 1. Actuators (P01–P06): the most important decisions

**Z (P01).** The THK KR20 with a 1 mm lead is a real, stocked product. Stock PNs seen through Oriental Motor's THK listing:

- KR2001A-0030/-0080/-0130
- accuracy suffix `0` (normal), `H0` (high accuracy) or `P0` (precision)
- `-01A0` = no cover, `-11A0` = cover

No 50 mm stock stroke was seen, so **KR2001A-0080-P0-01A0 (or -H0-)** is the lean. The 80 mm stroke gives 30 mm of margin for touch-off and capillary change. Monotaro lists KR2001A semi-order items, so the part can be bought in Japan. THK sells a "KR20 Direct Motor Mount" for NEMA17.

- **Unverified:** the numeric repeatability per KR grade. The THK "Accuracy Standards (KR)" page exists but its values were not visible. Do not quote ±0.003 for KR20 until the THK table is read.
- **Price not found.** The only figure was a used unit on eBay (~USD 108 + shipping).
- Alternatives:
  - MISUMI LX20, lead 1 (LX2001P). Repeatability ±0.005 (high grade) / ±0.003 (precision), from the MISUMI LX20 PDF excerpt.
  - Oriental DRS2 guide type with brake and AZ absolute encoder. Repeatability ±0.01 (rolled) / ±0.003 (ground). This is the "industrial, closed-loop" route, but it brings its own driver and does not use the TMC5160 controller. The exact DRS2 PN (lead, stroke, brake) must be configured; the listing PNs seen (DRSM42RG-04B2AZMK) do not reveal the lead.

**X (P02).** Lean **MISUMI LX26, lead 2, precision grade (LX2602P), 150 mm stroke**, or **THK KR2602A-0110-P0-01A0** (110 mm).

- Why not 100 mm: the stroke would equal the required travel exactly, leaving no margin to the mechanical stops.
- LX2602/LX2605 is available in 100 and 150 mm strokes, repeatability ±0.005 / ±0.003 (MISUMI PDF excerpt). One real PN was seen: LX2602-B1-A2625-100.
- MISUMI Japan base price range for LX26: **JPY 43,000–66,600** (search excerpt, approximate).

**Y (P03).** Stroke ≥30 mm, but Y carries the whole X cantilever (≈2.5–3 kg with a large overhang). A width-26 class body is therefore the safer choice (LX26 or KR26, shortest stroke ≥50 mm). The shortest stock strokes were **not verified** (KR26: only 110/160/210 seen). A moment-load check (Mp/My) against the carriage rating is still needed.

**Motors (P04/P05).** Oriental PKP244/PKP245 (42 mm; PKP244 holding torque 0.42 N·m). A brake version exists (legacy PKP244MD15M). Per doc 03 §5, no brake is needed with a 1 mm lead at 0.3 kg; keep the brake as an option. Detent torque was not found.

**Budget signal.** Industrial stages on all three axes (KR20 + 2 × LX26/KR26) plausibly consume **JPY 150–230k** before motors, controller, frame and holder. This is an estimate from the LX26 price range only. Hitting ~JPY 200k for the full picker probably means either:

- Arch. B on Y (doc 04 allows it), or
- accepting ~JPY 250–350k in total.

Reliability-over-price favours the second.

**Lead-time risk.** THK KR is often built to order (semi-order at Monotaro), so expect 2–6 weeks (unverified). MISUMI LX is usually a short, fixed lead time. Oriental ships from Japanese stock.

## 2. Microscope side (P07–P09): longest lead times

**Motorised stage (P07).**

- **Märzhäuser SCANplus IM 120 × 80 for IX53/IX73/IX83, order no. 00-24-579-0000.** 2 mm ball screw with an integrated measuring system (excerpt of the Märzhäuser datasheet and order info).
- The same class of stage is sold through the Olympus/Evident channel as **M-MS-IX3-2-2**: 120 × 80 mm, 2 mm pitch, reproducibility 1 µm, accuracy 3 µm, 2000 g, controllers Tango / OSIS / OASIS (WolfLabs listing).
- **Prior ProScan H117E1XD / H117N1XD for IX3:** 114 × 75 mm, 1 mm ball screw, encoded (E) version. Travel confirmed by two sources. The margin over 99 × 63 is smaller but sufficient.
- **ASI MS-2000 flat-top** is listed as IX73-compatible. Its travel was reported as both 120 × 110 and 120 × 75, so it is **unverified**.
- **No Evident-native motorised stage other than the IX3-SSU (76 × 52, insufficient) was found.**
- No prices were found; all require a quote.
- Lean: SCAN IM 120 × 80, via Evident as M-MS-IX3-2-2 if the lab wants a single Evident support channel, or Prior H117E1XD if the lab already uses Prior. All three brands are supported by Micro-Manager.

**Stage controller (P08).** Stage-specific (Märzhäuser Tango, Prior ProScan III, ASI MS-2000). Usually quoted with the stage.

**IX-ULWCD (P09).** Olympus part 6-U220, NA 0.30, WD 73 mm, 4 positions for Ø29 mm devices (Spectra Services and LabX excerpts agree). Old US contract list price is ~USD 974 (NY) / USD 864 (VA 2010). Refurbished units are offered by Spectra Services.

- **Risk:** one excerpt says the IX-ULWCD is "not available in some areas". Ask Evident Japan now. If it is unavailable, the fallback is the tilted pillar with LED ring (doc 03 §8), or a refurbished unit.

## 3. Capillary holder and break-away (P10–P12)

- **No off-the-shelf holder covers 1.0/1.5/2.0 mm with a side port and a positive collet.**
  - The Eppendorf Universal Capillary Holder grip heads cover 1.0–1.1 (head 0), 1.2–1.3 (head 1) and 1.4–1.5 (head 2). No 2.0 mm head was seen.
  - Narishige HI-7/HI-9 take 1.0 mm only.
  - The WPI MPH series (MPH3/4/6S) and the Warner Q-series with port (QSW-A15P = 1.5 mm, QSW-T20P = 2.0 mm) cover the sizes, but they clamp with O-rings or gaskets. Doc 03 rejects friction-only clamping as the primary fixation.
  - These are still useful for early pick tests.
- **Custom collet (lean).** A turned body using standard **Rego-Fix ER8 collets Ø1.0 / 1.5 / 2.0** (0.5 mm clamping range each, ~USD 45 each at retail), with a separate face seal and a 1/4-28 flat-bottom side port. The port then takes the IDEX XP-235X fitting directly.
  - **Risk 1:** an ER8 nut is likely larger than the Ø10 mm envelope (typical ~12–16 mm, **unverified**). Re-run `analysis.py` with a larger `HOLDER_D`.
  - **Risk 2:** steel collets can chip glass. Use a thin polymer sleeve or a torque limit, and test.
- **Break-away (P12).** Thorlabs **KB25/M**: 16 N (3.6 lbf) magnetic hold, ball/V-groove, USD 75.60 list. KB50/M holds 6.25 lbf. Lean KB25/M for the 0.3 kg Z group; Thorlabs Japan stocks it. Check that the release force at the tip (115 mm lever) protects the plate and does not release during landing.

## 4. Frame and custom parts (P13–P20, P37)

- MISUMI **HFS8-8080**: 4.57 kg/m, USD 43.60/m (MISUMI US excerpt). HFS8-4080 exists (price not seen). Order with milled or tapped ends.
- Base plate, angle blocks, dog-leg arm and brackets: **MISUMI meviy** (upload STEP for an instant quote; ships in as little as 1 day for simple parts). Only freeze after the actuator PNs (hole patterns) and M1/M15 are known.

## 5. Fluidics and consumables (P21–P27)

**Glass.**

| Class | Candidates |
|---|---|
| S (1.0 mm) | WPI 1B100-4; Narishige G-1 (1.0/0.6, 90 mm, 500/pk; Japanese maker) |
| M (1.5 mm) | WPI 1B150-4; Sutter B150-86-10 |
| L (2.0 mm) | WPI 1B200-4 |
| L′ (2.00/1.56 thin wall) | Sutter B200-156-10 (confirmed); WPI thin-wall no-filament 2.00/1.56, 10 cm × 250 and 15 cm × 100, exact PN (probably TW200-4) **unverified** |

Japanese stock of the thin-wall glass is unknown.

**Tubing and fittings.** IDEX FEP 1/16" × 0.030" natural, 50 ft = **1520L** (verified). IDEX **XP-235X** PEEK flangeless 1/4-28 FB fitting (USD 62.23 for a 10-pack on the IDEX store). The ferrule PN P-200X was not confirmed in this session.

**Pump interface.** Use IDEX Luer adapters (female Luer to 1/4-28), exact PN to configure, for Harvard syringes. Tecan Cavro valves are generally 1/4-28, to be confirmed per model (M17).

## 6. Electronics and safety (P28–P36)

**Controller.** Lean **Duet 3 Mainboard 6HC**. It has 6 on-board TMC5160 drivers (current boards all ship with 5160), 6.3 A peak, 9 IO ports and a G-code interface over USB/Ethernet, which matches the SpheroidPicker precedent. Price ~USD 231 at a US retailer (sold out). Buy genuine: AliExpress "Duet" listings (~USD 154) are clone risks.

- Alternatives:
  - BTT Octopus Pro + BTT TMC5160T Pro drivers (USD 133 per 4-pack).
  - ADI Trinamic TMCM-3110 (industrial, 3-axis, 9–52 V, up to 4 A, TMCL rather than G-code).
  - TMCM-3216 (3-axis, 2 A RMS, 10–30 V).

**Home switches.** Omron **EE-SX672/674** (5–24 V, NPN, Light-ON/Dark-ON selectable) or Panasonic PM-T45/PM-L25. Wire them fail-safe. Omron D2F-01L / D2VW-5-1HS micro switches (USD 3.6–5.5) are the mechanical NC option.

**PSU.** Mean Well **LRS-150-24** (24 V, 6.5 A), or SDR-120-24 for DIN rail.

**E-stop.** IDEC **XW1E-BV402M-R** (40 mm, 2NC) or XA1E-BV3U02R (16 mm, 2NC).

**Safety relay.** Omron **G9SE-201** (24 VDC, 2 safety NO, Cat.4/PLe) or IDEC HR6S-AF1C (~USD 357). **Unverified:** whether the G9SE contacts are rated for switching the driver VM bus, including capacitor inrush, directly. If not, add a force-guided relay or small DC contactor downstream.

**Cable chains.** igus E2i.15/B15i or E2.15, configured to width and radius. Prices are on request.

## 7. Top risks and uncertainties

1. **IX-ULWCD availability** (possible regional discontinuation). Confirm with Evident Japan before anything else; the whole near-vertical concept depends on it.
2. **Motorised stage lead time and cost** (quote-only; not in the picker budget). The choice also fixes the stage envelope that the tower must clear (freeze-gate item).
3. **Budget.** Industrial stages on all three axes likely push the picker above JPY 200k (my estimate: 250–350k).
4. **KR20 grade repeatability numbers and Y minimum strokes are unverified.** Read the THK KR accuracy table and the MISUMI LX26 stroke list (vendor pages blocked here) before choosing the grade.
5. **Holder envelope with ER8 collets** is probably larger than Ø10 mm. This changes the light-cone and condenser-clearance numbers, so re-run the analysis.

## 8. URLs used

- https://catalog.orientalmotor.com/item/linear-actuators-linear-slides-only/thk-lm-guide-actuator-kr20/kr2001a-0080-0-01a0
- https://catalog.orientalmotor.com/item/linear-actuators-linear-slides-only/thk-lm-guide-actuator-kr20/kr2001a-0080-h0-01a0
- https://catalog.orientalmotor.com/item/linear-actuators-linear-slides-only/thk-lm-guide-actuator-kr20/kr2001a-0030-p0-01a0
- https://catalog.orientalmotor.com/viewitems/linear-actuators-linear-slides-only/thk-lm-guide-actuator-kr20
- https://catalog.orientalmotor.com/item/linear-actuators-linear-slides-only/thk-lm-guide-actuator-kr26/kr2602a-0110-0-01a0
- https://www.thk.com/jp/en/products/lm_guide_actuator/full_ball/kr20/
- https://www.thk.com/jp/en/products/lm_guide_actuator/selection/0008/
- https://www.thk.com/jp/en/products/lm_guide_actuator/full_ball/kr20/ab_direct_standard/
- https://tech.thk.com/en/products/pdf_download.php?file=E_02_LMGuideActuator.pdf
- https://www.thkstore.com/kr20-direct-motor-mount.html
- https://www.thkstore.com/skr20-motor-wrap-3-o-clock.html
- https://www.monotaro.com/p/1564/1826/
- https://www.monotaro.com/p/1574/3229/
- https://www.ebay.com/itm/224442289353
- https://us.misumi-ec.com/pdf/fa/2014/P1_0417.pdf
- https://us.misumi-ec.com/vona2/detail/110300075020/
- https://us.misumi-ec.com/vona2/detail/110300075270/
- https://in.misumi-ec.com/pdf/fa/2014/p1_421_001_p1_423.pdf
- https://jp.misumi-ec.com/maker/misumi/mech/special/actuator_portal/lx/detail/
- https://www.radwell.com/en-US/Buy/MISUMI/MISUMI/LX2602-B1-A2625-100/
- https://us.misumi-ec.com/vona2/detail/110302392540/
- https://www.orientalmotor.com/linear-actuators/compact-linear-actuators-drs-series-absolute-encoder.html
- https://catalog.orientalmotor.com/item/all-categories-legacy-products/42mm-guide-drs-absolute-linear-actuators/drsm42rg-04b2azmk-azd-k
- https://catalog.orientalmotor.com/item/2-phase-bipolar-stepper-motors/42mm-pkp-series-2-phase-bipolar-stepper-motors/pkp244d15a2
- https://catalog.orientalmotor.com/item/42mm-frame-stepper-motors/42mm-pkp-series-2-phase-bipolar-stepper-motors/pkp245d15a2
- https://catalog.orientalmotor.com/item/all-categories-legacy-products/legacy-pkp-series-2-phase-bipolar-stepper-motors/pkp244md15m-1
- https://www.orientalmotor.com/stepper-motors/2-phase-stepper-motors-pkp-series.html
- https://www.orientalmotor.com/products/pdfs/2018-2019/549%20PKP%20Series%20Catalog.pdf
- https://products.marzhauser.com/Datenblaetter/EN/48-24-581-0000_SCAN_IM_120_80_DICTA_EN.pdf
- https://products.marzhauser.com/en/data/scanplus-im-c5838
- https://products.marzhauser.com/en/data/scan-im-c5836
- https://scop-pro.com/index.php?controller=attachment&id_attachment=22
- https://www.wolflabs.co.uk/laboratory-equipment/miscellaneous-products/e0433735/10433840
- https://www.prior.com/product/proscan-h117e1xd-inverted-stage
- https://www.prior.com/product/proscan-h117n1xd-inverted-stage
- https://www.prior.com/product/proscan-hld117ix-linear-motor-stage
- https://www.prior.com/Content/Downloads/Evident-Olympus-IX73-inverted-microscope.pdf
- https://photos.labwrench.com/equipmentManuals/14699-5711.pdf
- https://www.asiimaging.com/products/stages/xy-inverted-stages/ms-2000-flat-top-xyz-automated-stage/
- https://www.asiimaging.com/products/stages/xy-inverted-stages/ms-2000-xyz-automated-stage/
- https://spectraservices.com/product/6-u220.html
- https://spectraservices.com/product/6-u220-u.html
- https://www.labx.com/item/olympus-ix-ulwcd-long-working-distance-condenser/DIS-41276-6-U220
- https://online.ogs.ny.gov/purchase/spg/pdfdocs/1260023072PL_OlympusAmerica.pdf
- https://krebsmicro.com/pdf/Olympus%20Price%20List_B.pdf
- https://www.tengrant.com/upLoad/file/20190331/IX73-IX83_system_chart.pdf
- https://www.wpiinc.com/var-3781-microelectrode-holder-mph6s
- https://wpiinc.com/products/var-3819-microelectrode-holder-mph3
- https://www.warneronline.com/q-series-holders-for-Warner-and-some-early-axon
- https://www.harvardapparatus.com/media/brochures/Warner_Microelectrode_Holders.pdf
- https://products.narishige-group.com/group1/HI-7/injection/english.html
- https://products.narishige-group.com/group1/HI-9/injection/english.html
- https://www.fishersci.pt/shop/products/grip-head-0/11886884
- https://www.eppendorf.com/product-media/doc/en/142967_Supplement-sheet/Eppendorf_Cell-Technology_Instructions-use_Universal-capillary-holder.pdf
- https://shop.fischerspindle.com/Collets/ER8/en
- https://www.freertool.com/products/9-pc-collet-set-7mm-5mm-er8-style-collet
- https://www.toolsengg.com/collets-64/er-collets/er-standard-collets/er8-standard-collets
- https://www.thorlabs.com/item/KB25_M
- https://www.thorlabs.com/thorproduct.cfm?partnumber=KB50/M
- https://www.thorlabs.com/kinematic-bases2
- https://cdn.meviy.misumi-ec.com/en_us-us/
- https://www.misumi.co.jp/english/news/press_240708
- https://www.misumi.co.jp/english/news/press_250512_3
- https://us.misumi-ec.com/pdf/fa/2010/p2319.pdf
- https://us.misumi-ec.com/vona2/detail/110302690740/
- https://us.misumi-ec.com/vona2/detail/110302691870/
- https://us.misumi-ec.com/vona2/detail/110302690310/
- https://it.misumi-ec.com/files/images/products/docs/nutsforaluminiumextrusions.pdf
- https://www.wpiinc.com/clientuploads/pdf/catalog/pages/capillaryglass.pdf
- https://wpiinc.com/products/var-1972-standard-glass-capillaries-2mm-od
- https://wpiinc.com/products/var-3709-thin-wall-glass-capillaries
- https://wpiinc.com/products/var-tw100-3-thin-wall-glass-capillaries-no-filament
- https://www.fishersci.com/shop/products/bor-glass-tubing-225-pk/NC9051667
- https://www.sutter.com/micropipette/glass-0-0
- https://www.autom8.com/shop/micropipette-fabrication/glass/borosilicate-glass1-5-x-0-86mm-x-10cm-250-pcs/
- https://products.narishige-group.com/group1/G-1_1.2_1.5_2_3/pipette/english.html
- https://www.tritechresearch.com/G-1.html
- https://www.idex-hs.com/store/product-detail/fep_tubing_1_16_od_x_030_id_natural_50ft/1520l
- https://www.idex-hs.com/store/fluidics/fluidic-connections/tubing/fluoropolymer-tubing/teflonr-fep-tubing.html
- https://www.idex-hs.com/store/product-detail/flangeless_fitting_short_peek_1_4_28_flat_bottom_for_1_16_od_natural_10_pack/xp-235x
- https://www.coleparmer.com/i/idex-flangeless-ferrule-blue-etfe-1-16-od-tubing-1-4-28-flat-bottom-10-pk/0193930
- https://www.idex-hs.com/store/products/fluidics/fluidic_connections/connectors/luer_adapters
- https://scipro.com/idex-fluidics-connectors-luer-adapters/
- https://docs.duet3d.com/Duet3D_hardware/Duet_3_family/Duet_3_Mainboard_6HC_Hardware_Overview
- https://www.duet3d.com/duet3mainboard6hc
- https://forum.duet3d.com/topic/28043/confused-about-duet3-boards-having-tmc2160-or-tmc5160
- https://www.aliexpress.com/item/1005001633960755.html
- https://biqu.equipment/products/tmc5160-pro-v1-0
- https://www.amazon.com/BIGTREETECH-TMC5160-Stepper-Drivers-heatsink/dp/B0B8HZXWPP
- https://dfh.fm/products/btt-ez5160-pro-stepper-motor-driver
- https://www.trinamic.com/products/modules/details/tmcm-3110/
- https://www.mouser.com/new/trinamic/trinamic-tmcm-3110-stepper-motor-drivers/
- https://www.analog.com/en/products/tmcm-3216.html
- https://www.ia.omron.com/product/item/2224/
- https://datasheet.octopart.com/EE-SX672-Omron-datasheet-134124.pdf
- https://industry.panasonic.com/global/en/products/fasys/sensor/micro/number/pm-t45
- https://industry.panasonic.com/global/en/products/fasys/sensor/micro/number/pm-l25
- https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf
- https://octopart.com/d2vw-5-1hs-omron-47505
- https://www.mouser.com/ProductDetail/MEAN-WELL/LRS-150-24?qs=vDxCgdWo2h%2Bym5KOpEI%2Bpw%3D%3D
- https://us.rs-online.com/product/mean-well/lrs-150-24/70696543/
- https://powersupplymall.com/products/mean-well-sdr-120-24-single-output-industrial-power-supply-120w-24v-din-rail
- https://us.rs-online.com/product/idec-corporation/xw1e-bv402m-r/70172752/
- https://www.newark.com/idec/xa1e-bv3u02-r/switch-emergency-stop-2nc-250vac/dp/05R0253
- https://www.tme.com/us/en-us/details/xa1e-bv3u02r/panel-mount-switches-standard-16mm/idec/
- https://www.ia.omron.com/products/family/3419/
- https://www.digikey.com/en/products/detail/omron-automation-and-safety/G9SE-201/7495167
- https://automation.omron.com/en/us/products/family/G9SE
- https://www.igus.com/product/series-E2i-15
- https://www.igus.com/product/series-E2-15
- https://www.tme.com/us/en-us/details/b15i.050.075.0/cable-chains/igus/
