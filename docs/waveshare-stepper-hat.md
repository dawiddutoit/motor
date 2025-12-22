# Waveshare Stepper Motor HAT Rev2.1

The Waveshare Stepper Motor HAT is an expansion board for Raspberry Pi that provides dual stepper motor control using DRV8825 driver ICs.

## Overview

**Key Features:**
- Controls 2 stepper motors simultaneously
- DRV8825 drivers with up to 1/32 microstepping
- Supports motors up to 2.5A per phase
- 8.2V-28V motor power supply range
- On-board power switch

## Hardware Specifications

| Parameter | Value |
|-----------|-------|
| Motor channels | 2 |
| Driver IC | DRV8825 (×2) |
| Motor voltage | 8.2V - 28V DC |
| Current per coil | Up to 2.5A peak |
| Microstepping | 1, 1/2, 1/4, 1/8, 1/16, 1/32 |
| Logic voltage | 3.3V (from Pi) |
| Dimensions | 65mm × 56mm |

## Board Layout

```
  +-----------------------------------------------+
  |  [Power Switch]    [DC Jack 5.5x2.1mm]        |
  |                                               |
  |   [M1 Connector]              [M2 Connector]  |
  |     XH2.54-4P                   XH2.54-4P     |
  |                                               |
  |   +--------+                   +--------+     |
  |   |DRV8825 |                   |DRV8825 |     |
  |   |  (M1)  |                   |  (M2)  |     |
  |   +--------+                   +--------+     |
  |   [VREF POT]                   [VREF POT]     |
  |                                               |
  |   [40-pin GPIO Header - connects to Pi]       |
  +-----------------------------------------------+
```

## Power Supply

### Requirements

- **Voltage:** 12V DC recommended (8.2V - 28V range)
- **Current:** 5A recommended for two motors
- **Connector:** 5.5mm × 2.1mm barrel jack, center positive

### Power Switch

The on-board switch controls motor power only. The Pi continues running when the switch is OFF.

**Important:** Always turn off motor power before connecting/disconnecting motors.

## Motor Connections

### Connector Type

XH2.54-4P connectors (4-pin, 2.54mm pitch)

### Pin Assignment

| Motor 1 (M1) | Function | Motor 2 (M2) |
|--------------|----------|--------------|
| A1 | Coil A+ | A3 |
| A2 | Coil A- | A4 |
| B1 | Coil B+ | B3 |
| B2 | Coil B- | B4 |

### Wiring Colors (Common NEMA Motors)

| Manufacturer | Coil A (A+, A-) | Coil B (B+, B-) |
|--------------|-----------------|-----------------|
| Generic | Black, Green | Red, Blue |
| Pololu | Black, Green | Red, Blue |
| StepperOnline | Black, Green | Red, Blue |
| Wantai | Red, Green | Yellow, Blue |

**Note:** Always verify with your motor's datasheet. Incorrect wiring causes vibration instead of rotation.

### Identifying Coil Pairs

Use a multimeter on resistance mode:
1. Touch probe to any two wires
2. Low resistance (1-10Ω) = same coil
3. Open circuit = different coils

## GPIO Pin Mapping

### Motor 1 (M1)

| Function | BCM GPIO | Physical Pin |
|----------|----------|--------------|
| DIR | GPIO 13 | Pin 33 |
| STEP | GPIO 19 | Pin 35 |
| ENABLE | GPIO 12 | Pin 32 |
| MODE0 | GPIO 16 | Pin 36 |
| MODE1 | GPIO 17 | Pin 11 |
| MODE2 | GPIO 20 | Pin 38 |

### Motor 2 (M2)

| Function | BCM GPIO | Physical Pin |
|----------|----------|--------------|
| DIR | GPIO 24 | Pin 18 |
| STEP | GPIO 18 | Pin 12 |
| ENABLE | GPIO 4 | Pin 7 |
| MODE0 | GPIO 21 | Pin 40 |
| MODE1 | GPIO 22 | Pin 15 |
| MODE2 | GPIO 27 | Pin 13 |

## Rev2.1 Specific Notes

### Enable Pin Logic (CRITICAL)

**Rev2.1 uses inverted enable logic:**
- Enable pin HIGH = motor enabled (driver active)
- Enable pin LOW = motor disabled (driver off)

This is the opposite of the original Rev2.0 and some other driver boards.

The motor-control library handles this automatically:
```python
def enable(self):
    lgpio.gpio_write(self._chip, self._pins["enable"], 1)  # HIGH to enable

def disable(self):
    lgpio.gpio_write(self._chip, self._pins["enable"], 0)  # LOW to disable
```

### Version Identification

Check the silkscreen near the GPIO header for version marking:
- "Stepper Motor HAT (B) Rev2.1"

## Microstepping Configuration

Set microstepping by controlling MODE0, MODE1, MODE2 pins:

| Mode | MODE2 | MODE1 | MODE0 | Steps/Rev (200-step motor) |
|------|-------|-------|-------|---------------------------|
| Full | 0 | 0 | 0 | 200 |
| 1/2 | 0 | 0 | 1 | 400 |
| 1/4 | 0 | 1 | 0 | 800 |
| 1/8 | 0 | 1 | 1 | 1,600 |
| 1/16 | 1 | 0 | 0 | 3,200 |
| 1/32 | 1 | 0 | 1 | 6,400 |

## Current Adjustment

Each DRV8825 has a potentiometer for current limit adjustment.

### Setting Procedure

1. **Power off** the motor supply
2. Locate the small potentiometer near each DRV8825
3. Measure voltage at VREF point (potentiometer center pin)
4. Calculate: `Current (A) = VREF (V) × 2` (for 0.1Ω sense resistors)
5. Adjust clockwise to increase, counter-clockwise to decrease

### Recommended Settings

| Motor | Rated Current | Target VREF |
|-------|---------------|-------------|
| NEMA 14 (0.4A) | 0.4A | 0.2V |
| NEMA 17 (1.0A) | 1.0A | 0.5V |
| NEMA 17 (1.5A) | 1.5A | 0.75V |
| NEMA 17 (2.0A) | 2.0A | 1.0V |
| NEMA 23 (2.0A) | 2.0A | 1.0V |

**Warning:** Setting current too high causes motor overheating and driver thermal shutdown.

## Assembly

### Mounting to Raspberry Pi

1. Align the HAT's 40-pin connector with the Pi's GPIO header
2. Press down firmly and evenly
3. Use standoffs (M2.5) for mechanical support

### Motor Connection

1. Turn off motor power switch
2. Insert motor cable into appropriate connector (M1 or M2)
3. Ensure cable is fully seated
4. Turn on motor power

## Using with motor-control Library

### Basic Usage

```python
from motor_control import StepperMotor, MicrostepMode

# Initialize motor 1 with 1/16 microstepping
with StepperMotor(motor=1, steps_per_rev=200) as motor:
    motor.rotate(degrees=360, rpm=60)
```

### Both Motors

```python
from motor_control import StepperMotor

motor1 = StepperMotor(motor=1)
motor2 = StepperMotor(motor=2)

motor1.enable()
motor2.enable()

motor1.rotate(degrees=90, rpm=30)
motor2.rotate(degrees=-90, rpm=30)  # Opposite direction

motor1.cleanup()
motor2.cleanup()
```

## Troubleshooting

### Motor Doesn't Move

1. **Check power:** Is 12V supply connected and switch ON?
2. **Check enable:** Rev2.1 requires HIGH to enable
3. **Check wiring:** Verify motor connector is fully seated
4. **Check current:** VREF might be too low

### Motor Vibrates

- **Cause:** Coil wires swapped
- **Fix:** Swap A1↔A2 or B1↔B2 at connector

### Motor Runs Hot

- **Cause:** Current too high
- **Fix:** Reduce VREF potentiometer setting

### Driver Shuts Down

- **Cause:** Thermal protection activated
- **Fix:**
  - Reduce current limit
  - Add heatsink to DRV8825
  - Improve ventilation

### Erratic Movement

- **Cause:** Loose connections or EMI
- **Fix:**
  - Check all connections
  - Use shielded motor cables
  - Add decoupling capacitor on power input

## Schematic Notes

Key circuit elements (from Rev2.1 schematic):

- **Sense resistors:** 0.1Ω (sets current scale)
- **Decay mode:** Connected for mixed decay
- **Logic supply:** 3.3V from Pi GPIO header
- **nSLEEP/nRESET:** Directly connected together, active

## References

- [Waveshare Stepper Motor HAT Wiki](https://www.waveshare.com/wiki/Stepper_Motor_HAT)
- [HAT Schematic Rev2.1](./stepper-motor-hat-schematic-rev2.1.pdf)
- [Demo Code](./stepper-motor-hat-code.zip)
- [DRV8825 Driver Documentation](./drv8825-driver.md)
