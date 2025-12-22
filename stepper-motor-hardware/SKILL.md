---
name: stepper-motor-hardware
description: "Hardware reference for controlling NEMA stepper motors via Waveshare Stepper Motor HAT Rev2 on Raspberry Pi 4. Use when working with GPIO pins, DRV8825 driver settings, microstepping configuration, motor wiring, or troubleshooting stepper motor issues. Covers lgpio library usage, timing requirements, and current regulation."
---

# Stepper Motor Hardware Reference

Quick reference for Waveshare Stepper Motor HAT Rev2 with DRV8825 drivers on Raspberry Pi 4.

## Quick Reference Tables

### GPIO Pin Mapping (BCM)

| Function | Motor 1 | Motor 2 |
|----------|---------|---------|
| Direction | 13 | 24 |
| Step | 19 | 18 |
| Enable | 12 | 4 |
| Mode M0 | 16 | 21 |
| Mode M1 | 17 | 22 |
| Mode M2 | 20 | 27 |

### Microstepping Modes

| Mode | M0 | M1 | M2 | Steps/Rev |
|------|----|----|-----|-----------|
| Full | 0 | 0 | 0 | 200 |
| 1/2 | 1 | 0 | 0 | 400 |
| 1/4 | 0 | 1 | 0 | 800 |
| 1/8 | 1 | 1 | 0 | 1600 |
| 1/16 | 0 | 0 | 1 | 3200 |
| 1/32 | 1 | 0 | 1 | 6400 |

### Critical Settings

| Setting | Value | Note |
|---------|-------|------|
| Enable pin | HIGH | Rev2.1 inverted logic |
| GPIO chip | 0 (Pi4) / 4 (Pi5) | Auto-detect in code |
| Dir setup time | 5us | Before stepping |
| Enable delay | 10ms | After enabling |
| Motor voltage | 12-24V | Via barrel jack |

## Minimal Code Example

```python
import lgpio
import time

chip = lgpio.gpiochip_open(0)  # Pi 4
pins = {"dir": 13, "step": 19, "enable": 12, "mode": (16, 17, 20)}

# Configure pins
for pin in [pins["dir"], pins["step"], pins["enable"]] + list(pins["mode"]):
    lgpio.gpio_claim_output(chip, pin, 0)

# Set 1/16 microstepping
lgpio.gpio_write(chip, pins["mode"][0], 0)  # M0
lgpio.gpio_write(chip, pins["mode"][1], 0)  # M1
lgpio.gpio_write(chip, pins["mode"][2], 1)  # M2

# Enable and step
lgpio.gpio_write(chip, pins["enable"], 1)  # HIGH for Rev2.1
time.sleep(0.01)
lgpio.gpio_write(chip, pins["dir"], 1)  # CW
time.sleep(0.000005)

for _ in range(3200):  # One revolution at 1/16
    lgpio.gpio_write(chip, pins["step"], 1)
    time.sleep(0.0005)
    lgpio.gpio_write(chip, pins["step"], 0)
    time.sleep(0.0005)

lgpio.gpio_write(chip, pins["enable"], 0)
lgpio.gpiochip_close(chip)
```

## Speed Limits (US-17HS4401S @ 24V)

| Microstep | Max RPM | Limiting Factor |
|-----------|---------|-----------------|
| Full/1/4 | ~500-600 | Motor inductance |
| 1/16 | ~187 | Python timing |
| 1/32 | ~93 | Python timing |

For max speed use 1/4 microstepping. For smooth motion use 1/16 at lower RPM.

## Detailed References

- [Raspberry Pi 4 GPIO](references/raspberry-pi-4-gpio.md) - Pinout, electrical specs, lgpio usage
- [DRV8825 Driver](references/drv8825-driver.md) - Microstepping, current regulation, timing
- [Waveshare HAT](references/waveshare-stepper-hat.md) - Wiring, enable logic, troubleshooting
- [US-17HS4401S Motor](references/us-17hs4401s-motor.md) - Motor specs, speed limits, wiring
