# Hardware Documentation

## Overview

This project uses a Raspberry Pi 4 with the Waveshare Stepper Motor HAT Rev2 to control NEMA 17 stepper motors for a pan-tilt camera system.

## Components

| Component | Model | Purpose |
|-----------|-------|---------|
| Single Board Computer | Raspberry Pi 4 | Main controller, runs AI camera and web UI |
| Motor Driver HAT | Waveshare Stepper Motor HAT Rev2.1 | Dual DRV8825 stepper drivers |
| Stepper Motors | NEMA 17 (1.8°/step) | Pan and tilt axis movement |
| AI Camera | Raspberry Pi AI Camera (IMX500) | Object detection and tracking |

## Waveshare Stepper Motor HAT Rev2

### Specifications

- **Drivers**: 2x DRV8825 stepper motor drivers
- **Microstepping**: Up to 1/32 step
- **Max Current**: 2.5A per phase (with heatsink)
- **Voltage**: 8.2V - 45V motor supply
- **Interface**: GPIO (directly mounted on Pi header)

### GPIO Pin Mapping (BCM Numbering)

#### Motor 1 (Pan Axis)

| Function | GPIO Pin | Description |
|----------|----------|-------------|
| Direction | GPIO 13 | HIGH = CW, LOW = CCW |
| Step | GPIO 19 | Rising edge triggers step |
| Enable | GPIO 12 | HIGH = enabled (Rev2.1) |
| M0 | GPIO 16 | Microstepping select bit 0 |
| M1 | GPIO 17 | Microstepping select bit 1 |
| M2 | GPIO 20 | Microstepping select bit 2 |

#### Motor 2 (Tilt Axis)

| Function | GPIO Pin | Description |
|----------|----------|-------------|
| Direction | GPIO 24 | HIGH = CW, LOW = CCW |
| Step | GPIO 18 | Rising edge triggers step |
| Enable | GPIO 4 | HIGH = enabled (Rev2.1) |
| M0 | GPIO 21 | Microstepping select bit 0 |
| M1 | GPIO 22 | Microstepping select bit 1 |
| M2 | GPIO 27 | Microstepping select bit 2 |

### Microstepping Configuration

The DRV8825 supports multiple microstepping modes controlled by M0, M1, M2 pins:

| Mode | M0 | M1 | M2 | Steps/Rev (1.8° motor) |
|------|----|----|----|-----------------------|
| Full Step | 0 | 0 | 0 | 200 |
| 1/2 Step | 1 | 0 | 0 | 400 |
| 1/4 Step | 0 | 1 | 0 | 800 |
| 1/8 Step | 1 | 1 | 0 | 1,600 |
| 1/16 Step | 0 | 0 | 1 | 3,200 |
| 1/32 Step | 1 | 0 | 1 | 6,400 |

**Default**: 1/16 microstepping (3,200 steps/rev) provides a good balance of smoothness and speed.

### Timing Requirements

| Parameter | Min | Typical | Unit |
|-----------|-----|---------|------|
| Step pulse width | 1.9 | 2 | µs |
| Step low time | 1.9 | 2 | µs |
| Direction setup time | 650 | - | ns |
| Enable setup time | - | 10 | ms |

### Current Limiting

The DRV8825 drivers have an adjustable current limit set via a potentiometer on the HAT.

**To set current limit:**
1. Measure voltage at VREF test point (small potentiometer)
2. Calculate: `I_max = VREF × 2`
3. For NEMA 17 motors (typically 1.5-2A), set VREF to 0.75-1.0V

**Warning**: Setting current too high will overheat motors and drivers. Start low and increase if motors skip steps.

## Raspberry Pi 4 Setup

### GPIO Library

This project uses `lgpio` for GPIO control (successor to RPi.GPIO with better performance).

```bash
# Install system package
sudo apt install python3-lgpio
```

### GPIO Chip Selection

| Pi Model | GPIO Chip |
|----------|-----------|
| Raspberry Pi 4 | Chip 0 |
| Raspberry Pi 5 | Chip 4 |

The library auto-detects the correct chip.

### Python Virtual Environment

Since `lgpio` is a system package, the virtual environment must access system packages:

```bash
cd motor-control
uv venv --system-site-packages
uv sync
```

## NEMA 17 Stepper Motors

### Typical Specifications

| Parameter | Value |
|-----------|-------|
| Step Angle | 1.8° (200 steps/rev) |
| Rated Current | 1.5 - 2.0 A/phase |
| Holding Torque | 40 - 60 N·cm |
| Shaft Diameter | 5mm |
| Frame Size | 42mm × 42mm |

### Wiring (4-wire bipolar)

NEMA 17 motors have two coils (A and B). Each coil has two wires:

| HAT Terminal | Wire | Coil |
|--------------|------|------|
| A1 | Black | Coil A |
| A2 | Green | Coil A |
| B1 | Red | Coil B |
| B2 | Blue | Coil B |

**Note**: Wire colors vary by manufacturer. Use a multimeter to identify coil pairs (wires from the same coil will show low resistance ~1-2Ω).

### Finding Coil Pairs

1. Measure resistance between all wire combinations
2. Two pairs will show ~1-2Ω (same coil)
3. Wires from different coils show infinite resistance

## Pan-Tilt Configuration

### Motor Assignment

| Axis | Motor | Function |
|------|-------|----------|
| Pan | Motor 1 | Horizontal rotation |
| Tilt | Motor 2 | Vertical rotation |

### Gear Ratio

With a 2:1 belt/pulley reduction (18T motor pulley, 36T axis pulley):

| Parameter | Without Reduction | With 2:1 Reduction |
|-----------|-------------------|-------------------|
| Steps/rev (1/16 µstep) | 3,200 | 6,400 |
| Degrees/step | 0.1125° | 0.05625° |
| Resolution | Good | Better |
| Speed | Faster | Slower |
| Torque | Lower | Higher |

### Soft Limits

Default software limits protect the mechanism:

| Axis | Min | Max |
|------|-----|-----|
| Pan | -180° | +180° |
| Tilt | -45° | +90° |

## Power Supply

### Requirements

| Rail | Voltage | Current | Purpose |
|------|---------|---------|---------|
| Motor | 12-24V | 3A+ | Stepper motors |
| Logic | 5V | 3A | Pi 4 via USB-C |

**Recommended**: Single 12V 5A supply for motors, separate 5V 3A USB-C for Pi.

### Power Sequencing

1. Power on Pi first (allows GPIO initialization)
2. Apply motor power second
3. Or use a single supply with proper regulation

## Safety Notes

1. **Never disconnect motors while powered** - Back-EMF can damage drivers
2. **Use heatsinks on DRV8825** - They run hot under load
3. **Start with low current** - Increase only if motors skip steps
4. **Enable pin** - Rev2.1 HAT uses HIGH to enable (opposite of some other boards)
5. **Motor heat** - Normal operating temperature up to 50-60°C

## Troubleshooting

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| Motor doesn't move | Enable pin not HIGH | Check enable GPIO is set to 1 |
| Motor vibrates but doesn't rotate | Coil wires swapped | Swap A1/A2 or B1/B2 |
| Motor skips steps | Current too low | Increase VREF |
| Motor overheats | Current too high | Decrease VREF |
| Jerky movement | Microstepping not set | Verify M0/M1/M2 pins |
| Wrong direction | Direction pin logic | Swap direction in software |

## References

- [Waveshare Stepper Motor HAT Wiki](https://www.waveshare.com/wiki/Stepper_Motor_HAT)
- [DRV8825 Datasheet](https://www.ti.com/lit/ds/symlink/drv8825.pdf)
- [lgpio Documentation](https://abyz.me.uk/lg/py_lgpio.html)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
