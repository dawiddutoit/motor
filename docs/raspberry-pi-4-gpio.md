# Raspberry Pi 4 GPIO Reference

This document covers the GPIO (General Purpose Input/Output) capabilities of the Raspberry Pi 4 Model B, specifically for motor control applications.

## Overview

The Raspberry Pi 4 Model B is built around the BCM2711 SoC (System on Chip), which provides 54 GPIO lines. The 40-pin header exposes 28 of these GPIO pins for user applications.

## 40-Pin Header Pinout

```
                    3V3  (1)  (2)  5V
          GPIO 2 (SDA1)  (3)  (4)  5V
         GPIO 3 (SCL1)  (5)  (6)  GND
              GPIO 4    (7)  (8)  GPIO 14 (TXD0)
                   GND  (9)  (10) GPIO 15 (RXD0)
             GPIO 17   (11) (12) GPIO 18 (PCM_CLK)
             GPIO 27   (13) (14) GND
             GPIO 22   (15) (16) GPIO 23
                  3V3  (17) (18) GPIO 24
   GPIO 10 (SPI0_MOSI) (19) (20) GND
    GPIO 9 (SPI0_MISO) (21) (22) GPIO 25
   GPIO 11 (SPI0_SCLK) (23) (24) GPIO 8 (SPI0_CE0)
                   GND (25) (26) GPIO 7 (SPI0_CE1)
          GPIO 0 (ID_SD) (27) (28) GPIO 1 (ID_SC)
              GPIO 5   (29) (30) GND
              GPIO 6   (31) (32) GPIO 12 (PWM0)
       GPIO 13 (PWM1)  (33) (34) GND
  GPIO 19 (PCM_FS)     (35) (36) GPIO 16
             GPIO 26   (37) (38) GPIO 20 (PCM_DIN)
                   GND (39) (40) GPIO 21 (PCM_DOUT)
```

## GPIO Pins Used by Stepper Motor HAT

The Waveshare Stepper Motor HAT uses the following GPIO pins (BCM numbering):

| Function     | Motor 1 | Motor 2 | Physical Pins |
|--------------|---------|---------|---------------|
| Direction    | GPIO 13 | GPIO 24 | 33, 18        |
| Step         | GPIO 19 | GPIO 18 | 35, 12        |
| Enable       | GPIO 12 | GPIO 4  | 32, 7         |
| Mode M0      | GPIO 16 | GPIO 21 | 36, 40        |
| Mode M1      | GPIO 17 | GPIO 22 | 11, 15        |
| Mode M2      | GPIO 20 | GPIO 27 | 38, 13        |

## Electrical Specifications

### Absolute Maximum Ratings

| Parameter | Value |
|-----------|-------|
| Maximum voltage on any GPIO pin | 3.3V |
| Maximum current per GPIO pin | 16mA |
| Maximum total GPIO current | 50mA |

### Recommended Operating Conditions

| Parameter | Min | Typical | Max | Unit |
|-----------|-----|---------|-----|------|
| Input LOW voltage (VIL) | - | - | 0.8 | V |
| Input HIGH voltage (VIH) | 1.3 | - | 3.3 | V |
| Output LOW voltage (VOL) | - | - | 0.4 | V |
| Output HIGH voltage (VOH) | 2.4 | - | - | V |

### Internal Pull-up/Pull-down Resistors

- All GPIO pins have programmable internal pull-up and pull-down resistors
- Typical resistance: 50-65 kOhm
- Default states vary by pin (check BCM2711 documentation for specifics)

## GPIO Modes

Each GPIO pin can be configured for different functions:

| Mode | Description |
|------|-------------|
| Input | Read digital signal (HIGH/LOW) |
| Output | Write digital signal (HIGH/LOW) |
| ALT0-ALT5 | Alternate functions (SPI, I2C, UART, PWM, etc.) |

## Hardware PWM Channels

The BCM2711 provides hardware PWM on specific pins:

| PWM Channel | GPIO Pins |
|-------------|-----------|
| PWM0 | GPIO 12, GPIO 18 |
| PWM1 | GPIO 13, GPIO 19 |

**Note:** GPIO 12, 13, 18, and 19 are used by the Stepper Motor HAT, so hardware PWM is not available when using the HAT. The motor control uses software-timed GPIO toggling instead.

## GPIO Access Libraries

### lgpio (Recommended for Pi 4)

The motor control software uses `lgpio`, which is the recommended library for Raspberry Pi 4:

```bash
sudo apt install python3-lgpio
```

lgpio provides:
- Direct GPIO control via `/dev/gpiochip0`
- No root access required (with proper group membership)
- Support for both Pi 4 (chip 0) and Pi 5 (chip 4)

### GPIO Chip Selection

```python
import lgpio

# Raspberry Pi 4
chip = lgpio.gpiochip_open(0)

# Raspberry Pi 5 (if chip 0 fails)
chip = lgpio.gpiochip_open(4)
```

## User Permissions

To access GPIO without root privileges:

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in for changes to take effect
```

## Power Considerations

### 3.3V Rail

- Maximum recommended current: 50mA (shared with all 3.3V peripherals)
- The Stepper Motor HAT does not draw power from the 3.3V rail for motor drive

### 5V Rail

- Connected directly to USB-C power input
- Can supply up to 500mA to peripherals (depends on power supply rating)
- The HAT uses an external 12V supply for motor power

## Signal Timing

For stepper motor control, timing considerations:

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Direction setup time | 200ns | 5us |
| Step pulse HIGH time | 1.9us | 500us |
| Step pulse LOW time | 1.9us | 500us |

The motor control software uses:
- Direction setup: 5us (`time.sleep(0.000005)`)
- Step pulse timing: Calculated from RPM setting

## References

- [BCM2711 ARM Peripherals Datasheet](./bcm2711-peripherals.pdf)
- [Raspberry Pi 4 Model B Product Brief](./raspberry-pi-4-datasheet.pdf)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
