# US-17HS4401S NEMA 17 Motor Reference

## Specifications

| Parameter | Value |
|-----------|-------|
| Model | US-17HS4401S |
| Type | NEMA 17 Bipolar |
| Step Angle | 1.8° |
| Steps/Revolution | 200 |
| Rated Voltage | 2.6V DC |
| Rated Current | 1.7A/phase |
| Phase Resistance | 1.5Ω ±10% |
| Phase Inductance | 2.8mH ±20% |
| Holding Torque | 43 N·cm (60 oz·in) |
| Detent Torque | 2.2 N·cm |
| Rotor Inertia | 54 g·cm² |
| Motor Weight | ~280g |
| Shaft Diameter | 5mm (D-cut) |
| Body Length | 40mm |
| Wire Length | 100cm (4-wire) |

## Wiring (Bipolar)

| Wire Color | Connection |
|------------|------------|
| Black | A+ (Coil A) |
| Green | A- (Coil A) |
| Red | B+ (Coil B) |
| Blue | B- (Coil B) |

## Maximum Speed

### Theoretical Limits (Inductance-Based)

Formula: `RPM = (60 × V × 1000) / (L_mH × 2 × I × steps)`

| Supply Voltage | Theoretical Max | Usable Max (80% torque) |
|----------------|-----------------|-------------------------|
| 12V | 378 RPM | 200-280 RPM |
| 24V | 756 RPM | 400-560 RPM |

### Python/lgpio Timing Limits

Python's `time.sleep()` has ~100µs minimum reliable resolution on Raspberry Pi.

| Microstep | Steps/Rev | Step Rate | Max RPM |
|-----------|-----------|-----------|---------|
| Full | 200 | 10kHz | 3000 |
| 1/2 | 400 | 10kHz | 1500 |
| 1/4 | 800 | 10kHz | 750 |
| 1/8 | 1600 | 10kHz | 375 |
| 1/16 | 3200 | 10kHz | 187 |
| 1/32 | 6400 | 10kHz | 93 |

### Practical Speed Limits

| Voltage | Microstep | Max Usable RPM | Limiting Factor |
|---------|-----------|----------------|-----------------|
| 12V | Full | 280 | Motor inductance |
| 12V | 1/16 | 187 | Python timing |
| 24V | Full | 560 | Motor inductance |
| 24V | 1/4 | 560 | Motor inductance |
| 24V | 1/16 | 187 | Python timing |
| 24V | 1/32 | 93 | Python timing |

**Recommendations:**
- For max speed: Use 24V supply + Full or 1/4 microstepping → **~500-600 RPM**
- For smooth motion: Use 1/16 microstepping → **~180 RPM max**
- For precision: Use 1/32 microstepping → **~90 RPM max**

## Torque vs Speed

Torque decreases as speed increases due to inductance limiting current rise time.

```
Torque (%)
100% |████████████
 80% |████████████████
 60% |████████████████████
 40% |████████████████████████
 20% |████████████████████████████
     +----------------------------> RPM
     0   100  200  300  400  500
```

At 24V:
- 0-100 RPM: ~100% rated torque
- 200 RPM: ~80% rated torque
- 400 RPM: ~50% rated torque
- 600 RPM: ~20% rated torque (risk of stalling under load)

## Current Setting

Set DRV8825 Vref for 1.7A (or lower for less heat):

```
Vref = Current × 0.2
```

| Target Current | Vref Setting |
|----------------|--------------|
| 1.0A (reduced) | 0.20V |
| 1.4A (80%) | 0.28V |
| 1.7A (full) | 0.34V |

## Code Example - Max Speed Test

```python
from motor_control import StepperMotor, MicrostepMode

# For maximum speed, use lower microstepping
with StepperMotor(motor=1, microstep_mode=MicrostepMode.QUARTER) as motor:
    # At 1/4 step with 24V, can achieve ~500 RPM
    motor.rotate(degrees=3600, rpm=500, direction="cw")  # 10 revolutions
```

## Sources

- [HandsOnTec 17HS4401S Datasheet](https://www.handsontec.com/dataspecs/17HS4401S.pdf)
- [Oriental Motor Speed-Torque Curves](https://www.orientalmotor.com/stepper-motors/technology/speed-torque-curves-for-stepper-motors.html)
