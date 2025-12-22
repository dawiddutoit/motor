# Waveshare Stepper Motor HAT Rev2 Reference

## Overview

Dual-channel stepper motor driver HAT for Raspberry Pi, featuring two DRV8825 drivers supporting NEMA 11/14/17/23 stepper motors.

## Rev2.1 Enable Logic

**Critical**: Rev2.1 HAT has INVERTED enable logic compared to standard DRV8825.

| State | Enable Pin | Motor |
|-------|------------|-------|
| Enabled | HIGH (1) | Running |
| Disabled | LOW (0) | Stopped/Free |

```python
# Enable motor (Rev2.1)
lgpio.gpio_write(chip, enable_pin, 1)

# Disable motor
lgpio.gpio_write(chip, enable_pin, 0)
```

## GPIO Pin Mapping (BCM)

### Motor 1 (M1)
| Function | GPIO Pin |
|----------|----------|
| Direction | 13 |
| Step | 19 |
| Enable | 12 |
| Mode M0 | 16 |
| Mode M1 | 17 |
| Mode M2 | 20 |

### Motor 2 (M2)
| Function | GPIO Pin |
|----------|----------|
| Direction | 24 |
| Step | 18 |
| Enable | 4 |
| Mode M0 | 21 |
| Mode M1 | 22 |
| Mode M2 | 27 |

**Python dict:**
```python
MOTOR_PINS = {
    1: {"dir": 13, "step": 19, "enable": 12, "mode": (16, 17, 20)},
    2: {"dir": 24, "step": 18, "enable": 4,  "mode": (21, 22, 27)},
}
```

## Power Supply

| Parameter | Specification |
|-----------|---------------|
| Motor voltage | 8.2V - 28V |
| Recommended | 12V - 24V |
| Current per channel | Up to 2.5A peak |
| Connector | 5.5mm x 2.1mm barrel jack |

**Warning**: Do not power motors from Pi's 5V rail.

## Wiring Diagram

```
Motor Connector (4-pin):
  [1] [2] [3] [4]
   A2  A1  B1  B2

Bipolar motor coil pairs:
  Coil A: A1-A2
  Coil B: B1-B2
```

## Troubleshooting

### Motor doesn't move
1. Check enable pin is HIGH (Rev2.1)
2. Verify power supply connected and adequate voltage
3. Confirm motor wiring (coil pairs)
4. Check microstep mode pins are set

### Motor vibrates but doesn't rotate
1. Incorrect coil wiring - swap A1/A2 or B1/B2
2. Step frequency too high - reduce RPM
3. Current limit too low - adjust potentiometer

### Motor skips steps
1. Speed too high for load/current
2. Increase current limit
3. Reduce acceleration
4. Use lower microstep mode for more torque

### Motor runs hot
1. Current limit too high
2. Reduce motor current via potentiometer
3. Add cooling or reduce duty cycle
4. Disable motor when not moving

### Driver overheating
1. Reduce motor current
2. Add heatsink to DRV8825
3. Improve ventilation
4. Lower duty cycle

### Unexpected direction
1. DIR pin polarity swapped - change direction in code
2. Or swap one coil pair physically

## NEMA Motor Specifications

| Motor | Steps/Rev | Step Angle | Typical Current |
|-------|-----------|------------|-----------------|
| NEMA 11 | 200 | 1.8 deg | 0.5-1.0A |
| NEMA 14 | 200 | 1.8 deg | 0.8-1.5A |
| NEMA 17 | 200 | 1.8 deg | 1.0-2.0A |
| NEMA 23 | 200 | 1.8 deg | 1.5-3.0A |

Some motors use 400 steps/rev (0.9 deg step angle) - check datasheet.
