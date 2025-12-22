# DRV8825 Stepper Driver Reference

## Overview

The DRV8825 is a bipolar stepper motor driver IC with up to 1/32 microstepping and 2.5A peak current per phase.

## Microstepping Modes

| Mode | M0 | M1 | M2 | Steps/Rev (200-step motor) |
|------|----|----|----|-----------------------------|
| Full | 0  | 0  | 0  | 200                         |
| 1/2  | 1  | 0  | 0  | 400                         |
| 1/4  | 0  | 1  | 0  | 800                         |
| 1/8  | 1  | 1  | 0  | 1600                        |
| 1/16 | 0  | 0  | 1  | 3200                        |
| 1/32 | 1  | 0  | 1  | 6400                        |

**Python enum:**
```python
class MicrostepMode(Enum):
    FULL = (0, 0, 0)
    HALF = (1, 0, 0)
    QUARTER = (0, 1, 0)
    EIGHTH = (1, 1, 0)
    SIXTEENTH = (0, 0, 1)
    THIRTYSECOND = (1, 0, 1)
```

## Timing Requirements

| Parameter | Min | Typ | Unit |
|-----------|-----|-----|------|
| Step pulse width | 1.9 | - | us |
| Direction setup time | 650 | - | ns |
| Enable setup time | - | 10 | ms |
| Wake from sleep | 1.7 | - | ms |

**Safe delays in code:**
```python
# Direction setup
time.sleep(0.000005)  # 5us (well above 650ns)

# Enable stabilization
time.sleep(0.01)      # 10ms

# Step pulse (half period for 1kHz stepping)
time.sleep(0.0005)    # 500us each half
```

## Current Regulation

### Setting Current Limit

Adjust potentiometer on driver board. Reference voltage (Vref) at potentiometer wiper:

```
Vref = Current_limit × 2 × Rsense
```

For typical 0.1 ohm sense resistors:
```
Vref = Current_limit × 0.2
```

| Motor Current | Vref Setting |
|---------------|--------------|
| 0.5A          | 0.10V        |
| 1.0A          | 0.20V        |
| 1.5A          | 0.30V        |
| 2.0A          | 0.40V        |

**Caution**: Start low and increase. Excessive current causes overheating.

## Pin Functions

| Pin | Function | Active State |
|-----|----------|--------------|
| STEP | Step input | Rising edge |
| DIR | Direction | HIGH/LOW |
| ENABLE | Driver enable | LOW (inverted on Rev2.1 HAT) |
| M0, M1, M2 | Microstep select | See table above |
| FAULT | Fault output | LOW on fault |
| SLEEP | Sleep mode | LOW to sleep |
| RESET | Reset | LOW to reset |

## Thermal Considerations

- Rated for 45V, 2.5A peak (1.5A continuous without heatsink)
- Thermal shutdown at ~150C junction temp
- Add heatsink for currents >1A
- Reduce current if driver is too hot to touch

## Fault Conditions

FAULT pin goes LOW on:
- Overcurrent
- Thermal shutdown
- Undervoltage

Recovery: cycle ENABLE or RESET pin.
