# Preliminary electrical architecture (not frozen; no software in this stage)

![electrical block diagram](img/electrical_block_diagram.png)

```mermaid
flowchart LR
  AC[Mains 100 V AC] --> PSU[24 V DC PSU ~150 W, fused]
  PSU --> ES[E-stop NC + safety relay / contactor<br/>cuts MOTOR power only]
  PSU --> LOGIC[5 V / 3.3 V logic]
  PC[PC - USB] --> CTL[Motion controller<br/>G-code / serial]
  LOGIC --> CTL
  ES --> DX[X driver TMC5160] & DY[Y driver TMC5160] & DZ[Z driver TMC5160]
  CTL -- SPI + step/dir --> DX & DY & DZ
  DX --> MX[X NEMA17]
  DY --> MY[Y NEMA17]
  DZ --> MZ[Z NEMA17 + optional brake]
  SW[X/Y/Z home NC<br/>optional far limits NC<br/>E-stop status] --> CTL
  IL[optional interlock] -.-> CTL
  PC -. RS-232/USB .-> PUMP[Syringe pump<br/>own PSU, off-frame]
  ES -- hardware stop / inhibit --> PUMP
  CTL -. stop command .-> PUMP
  ES -- power --> PV[NC pinch valve<br/>fallback]
  PC --> STG[Motorised stage controller W-B]
  ES -- stop input --> STG
```

The main decisions are below.

**Driver class.** TMC5160 rather than TMC2209. The TMC5160 has external MOSFETs, so it runs 24 V NEMA17s at 1.5–2 A with headroom. It has SPI configuration and diagnostics, and stealthChop gives smooth low-speed Z landing. The TMC2209 is adequate electrically for small NEMA17s, but it runs near its thermal limit at 1.5 A and is configured over UART.

**Controller.** Any PC-accessible, G-code-speaking 32-bit motion board that exposes SPI to TMC5160 drivers and ≥6 NC inputs. An industrial alternative is to use the actuator vendor's own drivers, such as the Oriental AZ driver for a DRS2 Z axis. This follows the SpheroidPicker precedent of a G-code serial controller (S28).

**Home and reference switches.** All are normally-closed (fail-safe), so a broken wire reads as "triggered".
- X: outboard end. Y: front end.
- Z: **two switches**.
  - The **reference switch** is one physical switch on the Z body. It trips when the arm bottom is at {{Z_REF_ARM_BOTTOM:.1f}} mm above the stage datum, i.e. with the head top {{Z_REF_MARGIN:.0f}} mm below the lowest condenser front over all supported plates. It is set from M8 at installation. At that height the arm clears the condenser at every XY. Because the angle blocks change only the tip, not the arm, the same switch serves all heads; the tip lies inside each head's safe-Z corridor: {{ZREF_TIP_R08:.2f}} / {{ZREF_TIP_V20:.2f}} / {{ZREF_TIP_V30:.2f}} mm above the stage top for the 8° / 20° / 30° blocks (corridors in `03_architecture.md` §5).
  - The **top limit switch** is an over-travel stop only. It is *not* a safe position: near the optical axis, Z at the top drives the arm into the condenser.

**Homing order.** Z rises slowly to the reference switch (inside the corridor). X then moves to park (+{{WB_X_MAX}} mm, outside the condenser). Only then may Z go higher, and Y homes. After a power loss the tip may still be in a well; this order lifts it vertically out of the well without dragging it sideways and without reaching the condenser. A closed-loop absolute Z (D5, e.g. DRS2) makes this recovery independent of switches.

**Far limits.** Optional NC switches plus firmware soft limits. The actuators' own mechanical end stops are the hard limit.

**E-stop.** It removes motor power through a contactor. Logic stays powered so the controller latches and reports the fault. Z does not fall (see `03_architecture.md` §5). The E-stop must also stop **the pump and the motorised stage**, because a running pump keeps aspirating or dispensing and a moving stage drags the plate under the tip.

**Pump stop on E-stop (issue #8).** The pump keeps its own power supply, but its motion must stop on E-stop. Use the first option the chosen pump supports, in this order:

1. a **hardware stop / inhibit input** on the pump, wired to a spare NC contact of the safety relay;
2. a dedicated digital "stop" or "external trigger" input, driven by the relay;
3. a **controller stop command** over RS-232/USB **plus** a normally-closed pinch valve on the line, powered through the E-stop circuit, so the line is closed when power drops even if the command is lost.

Cutting the pump's mains is the last resort: some pumps lose their position or state and may not stop the plunger cleanly. M17 records which interface the lab's pump offers.

**Motorised stage on E-stop (W-B).** The stage controller's stop/enable input is wired to the relay the same way. If it has none, the stage motor supply is switched by the contactor.

**Restart and recovery.** Releasing the E-stop does not restart anything. The operator acknowledges the fault on the PC. The controller then re-homes Z to the reference (tip vertically out of the well), X to park, then Y. The pump is re-enabled last, after the tubing and the capillary have been inspected. A capillary that was in a well at the stop is treated as possibly broken (see break-away below).

**Break-away mount is a kinematic repositioner, not a force limiter.** The magnetic kinematic mount under the arm lets the arm come off in a crash and go back on to about the same place. It does **not** limit the force on the capillary: at a hold force of about {{BREAKAWAY_HOLD_N:.0f}} N it releases at about {{BREAK_RELEASE_N:.2f}} N at the tip, above the estimated lateral breaking force of every capillary class ({{BREAK_MIN_N:.2f}}–{{BREAK_MAX_N:.2f}} N). It does protect the plate (below {{PLATE_FORCE_LIMIT:.0f}} N, placeholder):

{{BREAK_TABLE_MD}}

Capillaries are therefore consumables in a crash. If the capillary itself must survive, a compliant or low-force stage is needed at the holder (a spring-loaded flexure that deflects at well below 0.15 N), or current/torque-limited Z landing with contact detection. This is left open (not V1).

**Wiring.** Motor cables shielded; switch cables in separate, twisted pairs; both in the cable chains on the rear side of the moving groups; tubing on the front side (`03_…` §7).
