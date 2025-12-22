"""Test script for the Waveshare Stepper Motor HAT Rev2."""

import time

from .stepper import StepperMotor, MicrostepMode


def main():
    """Run basic motor tests."""
    print("Waveshare Stepper Motor HAT Rev2 - Test Script")
    print("=" * 50)
    print()

    motor_num = 1  # Change to 2 if using motor 2

    print(f"Initializing Motor {motor_num}...")
    motor = StepperMotor(
        motor=motor_num,
        steps_per_rev=200,  # Standard NEMA 17/23 with 1.8° step angle
        microstep_mode=MicrostepMode.SIXTEENTH,
    )

    try:
        print(f"Effective steps per revolution: {motor.effective_steps_per_rev}")
        print()

        # Enable motor
        print("Enabling motor driver...")
        motor.enable()
        time.sleep(0.5)

        # Test 1: Rotate one full revolution clockwise
        print("Test 1: Rotating 360° clockwise at 30 RPM...")
        motor.rotate(degrees=360, rpm=30, direction="cw")
        time.sleep(1)

        # Test 2: Rotate one full revolution counter-clockwise
        print("Test 2: Rotating 360° counter-clockwise at 60 RPM...")
        motor.rotate(degrees=360, rpm=60, direction="ccw")
        time.sleep(1)

        # Test 3: Small movements
        print("Test 3: Small 45° movements...")
        for i in range(8):
            direction = "cw" if i % 2 == 0 else "ccw"
            print(f"  Moving 45° {direction}...")
            motor.rotate(degrees=45, rpm=90, direction=direction)
            time.sleep(0.3)

        print()
        print("All tests completed successfully!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        print("Disabling motor and cleaning up...")
        motor.cleanup()
        print("Done.")


if __name__ == "__main__":
    main()
