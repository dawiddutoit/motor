# Motor Control

Control NEMA stepper motors via the Waveshare Stepper Motor HAT Rev2 on Raspberry Pi 4.

## Hardware Setup

### Requirements

- Raspberry Pi 4
- Waveshare Stepper Motor HAT Rev2.1
- 12V 5A power adapter (connected to HAT's DC jack)
- NEMA stepper motor (e.g., NEMA 17 with 1.8° step angle = 200 steps/rev)

### Wiring

The HAT uses XH2.54 4P connectors for motor connections:

| Motor | Pin | Connection |
|-------|-----|------------|
| M1 | A1, A2 | Coil A (typically Black, Green) |
| M1 | B1, B2 | Coil B (typically Red, Blue) |
| M2 | A3, A4 | Coil A |
| M2 | B3, B4 | Coil B |

**Important:** Check your motor's datasheet for the correct coil pairings. Incorrect wiring may cause the motor to vibrate instead of rotating.

### GPIO Pin Mapping (BCM)

| Function | Motor 1 | Motor 2 |
|----------|---------|---------|
| Direction | GPIO 13 | GPIO 24 |
| Step | GPIO 19 | GPIO 18 |
| Enable | GPIO 12 | GPIO 4 |
| Mode M0 | GPIO 16 | GPIO 21 |
| Mode M1 | GPIO 17 | GPIO 22 |
| Mode M2 | GPIO 20 | GPIO 27 |

**Rev2.1 Note:** The enable pin must be set HIGH to activate the motor driver.

## Installation

### Prerequisites

Ensure your user has GPIO access:

```bash
sudo usermod -a -G gpio $USER
# Log out and back in for changes to take effect
```

### Install System Dependencies

The lgpio library requires system packages:

```bash
sudo apt install python3-lgpio
```

### Install the Package

```bash
cd motor-control

# Create venv with access to system packages (for lgpio)
uv venv --system-site-packages

# Install the package
uv sync
```

## Usage

### Command Line

Run the test script:

```bash
uv run motor-test
```

Use the CLI for custom movements:

```bash
# One full rotation at 60 RPM
uv run motor-run --degrees 360 --rpm 60

# Half rotation counter-clockwise at 30 RPM
uv run motor-run --degrees -180 --rpm 30

# Use motor 2
uv run motor-run --motor 2 --degrees 90

# Continuous rotation (Ctrl+C to stop)
uv run motor-run --continuous --rpm 120

# Continuous for 10 seconds
uv run motor-run --continuous --rpm 60 --duration 10

# Direct step control with custom delay
uv run motor-run --steps 1600 --delay 0.0005

# Change microstepping mode
uv run motor-run --microstep full --degrees 360 --rpm 30
```

### Python API

```python
from motor_control import StepperMotor, MicrostepMode

# Using context manager (recommended)
with StepperMotor(motor=1, steps_per_rev=200) as motor:
    motor.rotate(degrees=360, rpm=60, direction="cw")

# Manual control
motor = StepperMotor(
    motor=1,
    steps_per_rev=200,
    microstep_mode=MicrostepMode.SIXTEENTH,
)

motor.enable()
motor.rotate(degrees=180, rpm=30, direction="ccw")
motor.disable()
motor.cleanup()
```

### Microstepping Modes

| Mode | Multiplier | Effective Steps (200-step motor) |
|------|------------|----------------------------------|
| FULL | 1x | 200 |
| HALF | 2x | 400 |
| QUARTER | 4x | 800 |
| EIGHTH | 8x | 1,600 |
| SIXTEENTH | 16x | 3,200 |
| THIRTYSECOND | 32x | 6,400 |

Higher microstepping = smoother motion but lower torque and max speed.

## Troubleshooting

### Motor doesn't move

1. Check power is connected to the HAT (12V to DC jack)
2. Verify the HAT power switch is ON
3. Ensure motor wiring is correct (coils paired properly)
4. Check if you're using Rev2.1 (enable pin must be HIGH)

### Motor vibrates but doesn't rotate

- Coil wires are likely swapped. Check motor datasheet and swap A1/A2 or B1/B2.

### Permission denied on GPIO

```bash
sudo usermod -a -G gpio $USER
# Then log out and back in
```

### "Cannot determine SOC peripheral base address"

You may need to run with sudo, or ensure lgpio is properly installed:

```bash
sudo apt install python3-lgpio
```

## API Reference

### StepperMotor

```python
StepperMotor(
    motor: int = 1,           # Motor number (1 or 2)
    steps_per_rev: int = 200, # Native steps per revolution
    microstep_mode: MicrostepMode = MicrostepMode.SIXTEENTH,
)
```

**Methods:**

- `enable()` - Enable motor driver
- `disable()` - Disable motor driver (reduces heat)
- `step(steps, direction="cw", delay=0.001)` - Move exact number of microsteps
- `rotate(degrees=360, rpm=60, direction="cw")` - Rotate by angle
- `rotate_continuous(rpm=60, direction="cw", duration=None)` - Continuous rotation
- `set_microstep_mode(mode)` - Change microstepping mode
- `cleanup()` - Release GPIO resources

**Properties:**

- `microstep_multiplier` - Current multiplier (1, 2, 4, 8, 16, or 32)
- `effective_steps_per_rev` - Total steps including microstepping

## License

MIT
