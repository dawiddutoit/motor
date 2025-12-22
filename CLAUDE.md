# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library for controlling NEMA stepper motors via the Waveshare Stepper Motor HAT Rev2 on Raspberry Pi 4. Uses the lgpio library for GPIO control.

## Commands

```bash
# Install (from motor-control directory)
cd motor-control
uv venv --system-site-packages  # Required for lgpio access
uv sync

# Run test script
uv run motor-test

# Run motor with CLI
uv run motor-run --degrees 360 --rpm 60
uv run motor-run --continuous --rpm 120
uv run motor-run --steps 1600 --delay 0.0005
```

## Architecture

```
motor-control/
├── src/motor_control/
│   ├── __init__.py      # Exports StepperMotor, MicrostepMode
│   ├── stepper.py       # Core motor control class using lgpio
│   ├── cli.py           # motor-run CLI entry point
│   └── test.py          # motor-test script
```

**StepperMotor class** (`stepper.py`): Main interface for motor control. Uses context manager pattern for GPIO resource management. Supports two motors with different GPIO pin mappings defined in `MOTOR_PINS`.

**MicrostepMode enum**: Defines microstepping modes (FULL through THIRTYSECOND) as GPIO pin state tuples for the DRV8825 driver.

## Hardware Notes

- lgpio is a system package (`sudo apt install python3-lgpio`), hence `--system-site-packages` for venv
- GPIO chip 0 for Pi 4, chip 4 for Pi 5 (auto-detected)
- Enable pin must be HIGH for Rev2.1 HAT
- Motor 1 uses GPIO 13/19/12 (dir/step/enable), Motor 2 uses GPIO 24/18/4
