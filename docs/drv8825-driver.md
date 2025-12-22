# DRV8825 Stepper Motor Driver

The DRV8825 is a bipolar stepper motor driver IC manufactured by Texas Instruments. It's the motor driver used on the Waveshare Stepper Motor HAT Rev2.

## Overview

The DRV8825 provides:
- Up to 2.5A peak current per coil
- 1/32 microstepping resolution
- Built-in current regulation
- Overcurrent and thermal protection

## Key Specifications

| Parameter | Min | Typical | Max | Unit |
|-----------|-----|---------|-----|------|
| Motor supply voltage (VMOT) | 8.2 | - | 45 | V |
| Logic supply voltage (VCC) | 2.5 | 3.3 | 5.25 | V |
| Output current (per H-bridge) | - | - | 2.5 | A |
| RMS current (per H-bridge) | - | - | 1.75 | A |
| Operating temperature | -40 | - | 85 | °C |

## Pin Functions

### Control Inputs

| Pin | Function | Description |
|-----|----------|-------------|
| STEP | Step Input | Rising edge advances motor one step |
| DIR | Direction | LOW = forward, HIGH = reverse |
| nENBL | Enable (active LOW) | LOW enables outputs, HIGH disables |
| nRESET | Reset (active LOW) | LOW resets internal logic |
| nSLEEP | Sleep (active LOW) | LOW enters low-power sleep mode |

**Note:** The Waveshare HAT Rev2.1 inverts the enable logic, so HIGH enables the motor.

### Microstepping Mode Pins

| MODE0 | MODE1 | MODE2 | Step Mode |
|-------|-------|-------|-----------|
| 0 | 0 | 0 | Full step |
| 1 | 0 | 0 | Half step |
| 0 | 1 | 0 | 1/4 step |
| 1 | 1 | 0 | 1/8 step |
| 0 | 0 | 1 | 1/16 step |
| 1 | 0 | 1 | 1/32 step |
| 0 | 1 | 1 | 1/32 step |
| 1 | 1 | 1 | 1/32 step |

## Microstepping Explained

Microstepping divides each full step into smaller increments for smoother motion:

| Mode | Steps per Revolution | Degrees per Step | Notes |
|------|---------------------|------------------|-------|
| Full | 200 | 1.8° | Maximum torque |
| Half | 400 | 0.9° | Good balance |
| 1/4 | 800 | 0.45° | Smoother motion |
| 1/8 | 1,600 | 0.225° | Low vibration |
| 1/16 | 3,200 | 0.1125° | Very smooth |
| 1/32 | 6,400 | 0.05625° | Ultra smooth |

**Trade-offs:**
- Higher microstepping = smoother motion, lower vibration
- Higher microstepping = reduced torque, lower maximum speed
- 1/16 microstepping (default in motor-control) is a good balance

## Current Regulation

The DRV8825 uses PWM current regulation with an external sense resistor:

```
I_TRIP = V_REF / (5 × R_SENSE)
```

Where:
- `I_TRIP` = Trip current (peak current per coil)
- `V_REF` = Reference voltage (set by potentiometer on HAT)
- `R_SENSE` = Sense resistor value (typically 0.1Ω on the HAT)

### Setting Current Limit

On the Waveshare HAT, adjust the potentiometer to set the current:

1. Measure voltage at VREF test point (or potentiometer wiper)
2. Calculate: `I_MAX = V_REF / 0.5` (for 0.1Ω sense resistor)
3. Example: VREF = 0.5V → I_MAX = 1.0A per coil

**Recommended settings by motor size:**

| Motor Type | Rated Current | Recommended VREF |
|------------|---------------|------------------|
| NEMA 14 | 0.5-1.0A | 0.25-0.5V |
| NEMA 17 | 1.0-2.0A | 0.5-1.0V |
| NEMA 23 | 1.5-2.5A | 0.75-1.25V |

## Decay Modes

The DRV8825 supports multiple decay modes for current regulation:

| DECAY Pin | Mode | Description |
|-----------|------|-------------|
| LOW | Slow decay | Better for low speeds, more torque |
| HIGH | Fast decay | Better for high speeds, less heating |
| NC | Mixed decay | Automatic mode selection |

The Waveshare HAT typically uses mixed decay mode.

## Timing Requirements

### Step Input Timing

| Parameter | Min | Unit |
|-----------|-----|------|
| Step pulse HIGH time (t_WH) | 1.9 | µs |
| Step pulse LOW time (t_WL) | 1.9 | µs |
| Direction setup time | 200 | ns |
| Direction hold time | 200 | ns |

### Maximum Step Frequency

The maximum step frequency depends on motor inductance and supply voltage:

```
f_max ≈ V_MOTOR / (2 × L × I_MAX)
```

Typical maximum frequencies:
- Full step: ~10 kHz
- 1/16 microstepping: ~160 kHz (but motor limits apply)

## Protection Features

### Overcurrent Protection (OCP)

- Triggers at approximately 2.5A per coil
- Latched fault condition
- Clear by toggling nRESET or power cycle

### Thermal Shutdown (TSD)

- Activates at junction temperature ~150°C
- Automatic recovery when cooled
- Indicates overload or inadequate heat sinking

### Undervoltage Lockout (UVLO)

- Prevents operation below minimum supply voltage
- VMOT UVLO: 7.6V typical
- VCC UVLO: 2.25V typical

## Heat Dissipation

Power dissipation calculations:

```
P_TOTAL = P_OUTPUT + P_SWITCHING + P_QUIESCENT

P_OUTPUT ≈ I_RMS² × R_DS(ON) × 2  (for two H-bridges)
```

Where R_DS(ON) ≈ 0.35Ω typical for high-side + low-side FETs.

**Thermal management tips:**
- Use heatsink for currents > 1A continuous
- Ensure adequate airflow
- Reduce current when motors are stationary
- The motor-control library disables outputs when idle

## Wiring Diagram

```
         +--------+
  VMOT --|        |-- AOUT1 ──┐
   GND --|        |-- AOUT2 ──┼── Motor Coil A
         |        |           |
 nRESET--|        |-- BOUT1 ──┐
 nSLEEP--|        |-- BOUT2 ──┼── Motor Coil B
         |DRV8825 |           |
  STEP --|        |-- GND
   DIR --|        |
 nENBL --|        |
         |        |
 MODE0 --|        |-- VREF
 MODE1 --|        |-- nFAULT
 MODE2 --|        |
         |        |
   VCC --|        |
   GND --|        |
         +--------+
```

## Common Issues

### Motor Vibrates But Doesn't Rotate

- **Cause:** Incorrect coil wiring
- **Fix:** Identify coil pairs with multimeter (connected wires have low resistance) and swap if needed

### Motor Runs Hot

- **Cause:** Current limit too high
- **Fix:** Reduce VREF voltage

### Skipped Steps

- **Causes:**
  - Speed too high for load
  - Current limit too low
  - Insufficient supply voltage
- **Fixes:**
  - Reduce speed
  - Increase current (within motor rating)
  - Use higher voltage supply (up to 45V)

### Driver Overheating

- **Cause:** Insufficient cooling
- **Fix:** Add heatsink, improve airflow, reduce current

## References

- [DRV8825 Datasheet (TI)](./drv8825-datasheet.pdf)
- [TI DRV8825 Product Page](https://www.ti.com/product/DRV8825)
- [Application Note: Stepper Motor Driver Current Setting](https://www.ti.com/lit/an/slva555/slva555.pdf)
