"""Stepper motor control for Waveshare Stepper Motor HAT Rev2.

This module provides control for NEMA stepper motors connected to the
Waveshare Stepper Motor HAT Rev2 on Raspberry Pi.

GPIO Pin Mapping (BCM numbering):
---------------------------------
Motor 1 (M1):
    - Direction: GPIO 13
    - Step:      GPIO 19
    - Enable:    GPIO 12 (HIGH = enabled for Rev2.1)
    - Mode pins: GPIO 16, 17, 20 (M0, M1, M2)

Motor 2 (M2):
    - Direction: GPIO 24
    - Step:      GPIO 18
    - Enable:    GPIO 4 (HIGH = enabled for Rev2.1)
    - Mode pins: GPIO 21, 22, 27 (M0, M1, M2)
"""

import time
from enum import Enum
from typing import Literal

import lgpio


class MicrostepMode(Enum):
    """Microstepping modes for DRV8825 driver.

    Values represent (M0, M1, M2) pin states.
    """
    FULL = (0, 0, 0)       # 1 step = 1 full step
    HALF = (1, 0, 0)       # 1 step = 1/2 step
    QUARTER = (0, 1, 0)    # 1 step = 1/4 step
    EIGHTH = (1, 1, 0)     # 1 step = 1/8 step
    SIXTEENTH = (0, 0, 1)  # 1 step = 1/16 step
    THIRTYSECOND = (1, 0, 1)  # 1 step = 1/32 step


# GPIO pin definitions for each motor
MOTOR_PINS = {
    1: {
        "dir": 13,
        "step": 19,
        "enable": 12,
        "mode": (16, 17, 20),  # M0, M1, M2
    },
    2: {
        "dir": 24,
        "step": 18,
        "enable": 4,
        "mode": (21, 22, 27),  # M0, M1, M2
    },
}


class StepperMotor:
    """Control a stepper motor via the Waveshare Stepper Motor HAT Rev2.

    Args:
        motor: Motor number (1 or 2)
        steps_per_rev: Steps per revolution for your motor (typically 200 for 1.8° motors)
        microstep_mode: Microstepping mode (default: SIXTEENTH for smooth operation)

    Example:
        >>> motor = StepperMotor(motor=1, steps_per_rev=200)
        >>> motor.enable()
        >>> motor.rotate(degrees=360, rpm=60)
        >>> motor.disable()
        >>> motor.cleanup()
    """

    def __init__(
        self,
        motor: Literal[1, 2] = 1,
        steps_per_rev: int = 200,
        microstep_mode: MicrostepMode = MicrostepMode.SIXTEENTH,
    ):
        if motor not in (1, 2):
            raise ValueError("Motor must be 1 or 2")

        self.motor = motor
        self.steps_per_rev = steps_per_rev
        self._microstep_mode = microstep_mode
        self._pins = MOTOR_PINS[motor]
        self._enabled = False

        # Open GPIO chip (chip 0 for Pi 4, chip 4 for Pi 5)
        try:
            self._chip = lgpio.gpiochip_open(0)
        except lgpio.error:
            # Try chip 4 for Raspberry Pi 5
            self._chip = lgpio.gpiochip_open(4)

        # Configure all pins as outputs
        for pin_name in ["dir", "step", "enable"]:
            lgpio.gpio_claim_output(self._chip, self._pins[pin_name], 0)

        for mode_pin in self._pins["mode"]:
            lgpio.gpio_claim_output(self._chip, mode_pin, 0)

        # Set initial microstepping mode
        self.set_microstep_mode(microstep_mode)

    @property
    def microstep_multiplier(self) -> int:
        """Get the current microstep multiplier."""
        multipliers = {
            MicrostepMode.FULL: 1,
            MicrostepMode.HALF: 2,
            MicrostepMode.QUARTER: 4,
            MicrostepMode.EIGHTH: 8,
            MicrostepMode.SIXTEENTH: 16,
            MicrostepMode.THIRTYSECOND: 32,
        }
        return multipliers[self._microstep_mode]

    @property
    def effective_steps_per_rev(self) -> int:
        """Get effective steps per revolution including microstepping."""
        return self.steps_per_rev * self.microstep_multiplier

    def set_microstep_mode(self, mode: MicrostepMode) -> None:
        """Set the microstepping mode.

        Args:
            mode: Microstepping mode (FULL, HALF, QUARTER, EIGHTH, SIXTEENTH, THIRTYSECOND)
        """
        self._microstep_mode = mode
        m0, m1, m2 = mode.value
        mode_pins = self._pins["mode"]
        lgpio.gpio_write(self._chip, mode_pins[0], m0)
        lgpio.gpio_write(self._chip, mode_pins[1], m1)
        lgpio.gpio_write(self._chip, mode_pins[2], m2)

    def enable(self) -> None:
        """Enable the motor driver (Rev2.1 requires HIGH to enable)."""
        lgpio.gpio_write(self._chip, self._pins["enable"], 1)
        self._enabled = True
        time.sleep(0.01)  # Brief delay for driver to stabilize

    def disable(self) -> None:
        """Disable the motor driver (reduces power consumption and heat)."""
        lgpio.gpio_write(self._chip, self._pins["enable"], 0)
        self._enabled = False

    def step(self, steps: int, direction: Literal["cw", "ccw"] = "cw", delay: float = 0.001) -> None:
        """Move the motor a specific number of steps.

        Args:
            steps: Number of microsteps to move
            direction: "cw" for clockwise, "ccw" for counter-clockwise
            delay: Delay between steps in seconds (controls speed)
        """
        if not self._enabled:
            raise RuntimeError("Motor is not enabled. Call enable() first.")

        # Set direction (HIGH = one direction, LOW = other)
        dir_value = 1 if direction == "cw" else 0
        lgpio.gpio_write(self._chip, self._pins["dir"], dir_value)
        time.sleep(0.000005)  # Direction setup time

        step_pin = self._pins["step"]
        half_delay = delay / 2
        min_pulse = 0.000002  # 2μs minimum pulse width for DRV8825

        # Use perf_counter for accurate timing
        next_time = time.perf_counter()

        for _ in range(abs(steps)):
            lgpio.gpio_write(self._chip, step_pin, 1)
            # Busy-wait for accurate short delays
            pulse_end = time.perf_counter() + max(half_delay, min_pulse)
            while time.perf_counter() < pulse_end:
                pass
            lgpio.gpio_write(self._chip, step_pin, 0)

            # Schedule next step based on target time, not actual time
            next_time += delay
            wait_time = next_time - time.perf_counter()
            if wait_time > 0.001:
                time.sleep(wait_time - 0.0005)  # Sleep most of it, busy-wait the rest
            # Busy-wait for remaining time
            while time.perf_counter() < next_time:
                pass

    def rotate(
        self,
        degrees: float = 360,
        rpm: float = 60,
        direction: Literal["cw", "ccw"] = "cw",
    ) -> None:
        """Rotate the motor by a specified angle.

        Args:
            degrees: Degrees to rotate (default: 360 = one full revolution)
            rpm: Rotations per minute (speed)
            direction: "cw" for clockwise, "ccw" for counter-clockwise
        """
        # Calculate steps needed
        steps_per_degree = self.effective_steps_per_rev / 360
        steps = int(abs(degrees) * steps_per_degree)

        # Calculate delay from RPM
        # RPM -> RPS -> steps per second -> delay per step
        rps = rpm / 60
        steps_per_second = rps * self.effective_steps_per_rev
        delay = 1 / steps_per_second if steps_per_second > 0 else 0.001

        self.step(steps, direction, delay)

    def rotate_continuous(
        self,
        rpm: float = 60,
        direction: Literal["cw", "ccw"] = "cw",
        duration: float | None = None,
    ) -> None:
        """Rotate continuously at a specified speed.

        Args:
            rpm: Rotations per minute
            direction: "cw" for clockwise, "ccw" for counter-clockwise
            duration: Duration in seconds (None = run until interrupted)
        """
        rps = rpm / 60
        steps_per_second = rps * self.effective_steps_per_rev
        delay = 1 / steps_per_second if steps_per_second > 0 else 0.001

        dir_value = 1 if direction == "cw" else 0
        lgpio.gpio_write(self._chip, self._pins["dir"], dir_value)
        time.sleep(0.000005)

        step_pin = self._pins["step"]
        min_pulse = 0.000002  # 2μs minimum pulse width

        start_time = time.perf_counter()
        end_time = start_time + duration if duration else None
        next_time = start_time

        try:
            while True:
                if end_time and time.perf_counter() >= end_time:
                    break

                lgpio.gpio_write(self._chip, step_pin, 1)
                pulse_end = time.perf_counter() + min_pulse
                while time.perf_counter() < pulse_end:
                    pass
                lgpio.gpio_write(self._chip, step_pin, 0)

                next_time += delay
                wait_time = next_time - time.perf_counter()
                if wait_time > 0.001:
                    time.sleep(wait_time - 0.0005)
                while time.perf_counter() < next_time:
                    pass
        except KeyboardInterrupt:
            pass

    def cleanup(self) -> None:
        """Release GPIO resources."""
        self.disable()
        lgpio.gpiochip_close(self._chip)

    def __enter__(self) -> "StepperMotor":
        """Context manager entry."""
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.cleanup()
