# Motor Control Documentation

Hardware documentation and datasheets for the stepper motor control system.

## Documentation Files

### Markdown Guides

| Document | Description |
|----------|-------------|
| [Raspberry Pi 4 GPIO](./raspberry-pi-4-gpio.md) | GPIO pinout, electrical specs, and usage for motor control |
| [DRV8825 Driver](./drv8825-driver.md) | Stepper motor driver IC reference, microstepping, current control |
| [Waveshare Stepper HAT](./waveshare-stepper-hat.md) | HAT assembly, wiring, Rev2.1 specifics, troubleshooting |

### Datasheets (PDF)

| Document | Size | Description |
|----------|------|-------------|
| [raspberry-pi-4-datasheet.pdf](./raspberry-pi-4-datasheet.pdf) | 404K | Raspberry Pi 4 Model B specifications |
| [bcm2711-peripherals.pdf](./bcm2711-peripherals.pdf) | 1.3M | BCM2711 SoC peripheral documentation |
| [drv8825-datasheet.pdf](./drv8825-datasheet.pdf) | 1.4M | TI DRV8825 stepper motor driver IC |
| [stepper-motor-hat-manual.pdf](./stepper-motor-hat-manual.pdf) | 1010K | Waveshare Stepper Motor HAT user manual |
| [stepper-motor-hat-schematic-rev2.1.pdf](./stepper-motor-hat-schematic-rev2.1.pdf) | 420K | HAT circuit schematic |

### Demo Code

| Archive | Description |
|---------|-------------|
| [stepper-motor-hat-code.zip](./stepper-motor-hat-code.zip) | Waveshare demo code (C, Python2, Python3) |

## Quick Reference

### GPIO Pin Mapping (BCM)

| Function | Motor 1 | Motor 2 |
|----------|---------|---------|
| Direction | GPIO 13 | GPIO 24 |
| Step | GPIO 19 | GPIO 18 |
| Enable | GPIO 12 | GPIO 4 |
| Mode M0 | GPIO 16 | GPIO 21 |
| Mode M1 | GPIO 17 | GPIO 22 |
| Mode M2 | GPIO 20 | GPIO 27 |

### Microstepping Modes

| Mode | MODE2 | MODE1 | MODE0 | Steps/Rev |
|------|-------|-------|-------|-----------|
| Full | 0 | 0 | 0 | 200 |
| 1/2 | 0 | 0 | 1 | 400 |
| 1/4 | 0 | 1 | 0 | 800 |
| 1/8 | 0 | 1 | 1 | 1,600 |
| 1/16 | 1 | 0 | 0 | 3,200 |
| 1/32 | 1 | 0 | 1 | 6,400 |

### Current Limit Formula

```
Current (A) = VREF (V) × 2
```

Adjust the potentiometer on each DRV8825 to set VREF.

### Rev2.1 Enable Logic

**Enable pin must be HIGH to activate the motor driver.**

```python
lgpio.gpio_write(chip, enable_pin, 1)  # Enable motor
lgpio.gpio_write(chip, enable_pin, 0)  # Disable motor
```

## Hardware Setup Checklist

- [ ] Raspberry Pi 4 with Raspbian/Raspberry Pi OS
- [ ] Waveshare Stepper Motor HAT Rev2.1 mounted on GPIO header
- [ ] 12V 5A power supply connected to HAT DC jack
- [ ] NEMA stepper motor(s) connected with correct coil pairing
- [ ] Current limit adjusted via potentiometer for motor rating
- [ ] `python3-lgpio` system package installed
- [ ] User added to `gpio` group

## See Also

- [Motor Control Library README](../motor-control/README.md)
- [CLAUDE.md](../CLAUDE.md) - Development guide for this project
