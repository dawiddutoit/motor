# Raspberry Pi 4 GPIO Reference

## GPIO Chip Selection

| Pi Model | GPIO Chip |
|----------|-----------|
| Pi 4     | 0         |
| Pi 5     | 4         |

```python
import lgpio
try:
    chip = lgpio.gpiochip_open(0)  # Pi 4
except lgpio.error:
    chip = lgpio.gpiochip_open(4)  # Pi 5
```

## Electrical Specifications

| Parameter | Value |
|-----------|-------|
| Logic level | 3.3V |
| Max current per pin | 16mA |
| Max total GPIO current | 50mA |
| Input high threshold | >1.3V |
| Input low threshold | <0.8V |

**Warning**: GPIO pins are NOT 5V tolerant. Level shifting required for 5V logic.

## lgpio Library Usage

### Installation
```bash
sudo apt install python3-lgpio
```

### Pin Configuration
```python
# Claim pin as output (initial value 0)
lgpio.gpio_claim_output(chip, pin, 0)

# Claim pin as input
lgpio.gpio_claim_input(chip, pin)
```

### Read/Write Operations
```python
# Write to pin
lgpio.gpio_write(chip, pin, 1)  # HIGH
lgpio.gpio_write(chip, pin, 0)  # LOW

# Read from pin
value = lgpio.gpio_read(chip, pin)
```

### Cleanup
```python
lgpio.gpiochip_close(chip)
```

## BCM Pin Numbering

The Waveshare HAT uses BCM (Broadcom) numbering, not physical pin numbers.

| BCM | Physical | Function on HAT |
|-----|----------|-----------------|
| 4   | 7        | M2 Enable       |
| 12  | 32       | M1 Enable       |
| 13  | 33       | M1 Direction    |
| 16  | 36       | M1 Mode M0      |
| 17  | 11       | M1 Mode M1      |
| 18  | 12       | M2 Step         |
| 19  | 35       | M1 Step         |
| 20  | 38       | M1 Mode M2      |
| 21  | 40       | M2 Mode M0      |
| 22  | 15       | M2 Mode M1      |
| 24  | 18       | M2 Direction    |
| 27  | 13       | M2 Mode M2      |

## Virtual Environment Note

Since lgpio is a system package, create venv with system site-packages access:

```bash
uv venv --system-site-packages
```
