"""Command-line interface for motor control."""

import argparse
import sys

from .stepper import StepperMotor, MicrostepMode


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Control NEMA stepper motors via Waveshare Stepper Motor HAT Rev2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  motor-run --degrees 360 --rpm 60       # One full rotation at 60 RPM
  motor-run --degrees -180 --rpm 30      # Half rotation counter-clockwise
  motor-run --motor 2 --degrees 90       # 90° rotation on motor 2
  motor-run --continuous --rpm 120       # Continuous rotation until Ctrl+C
  motor-run --steps 1600 --delay 0.0005  # Direct step control
        """,
    )

    parser.add_argument(
        "--motor", "-m",
        type=int,
        choices=[1, 2],
        default=1,
        help="Motor number (1 or 2, default: 1)",
    )

    parser.add_argument(
        "--steps-per-rev", "-s",
        type=int,
        default=200,
        help="Steps per revolution for your motor (default: 200 for 1.8° motors)",
    )

    parser.add_argument(
        "--microstep",
        type=str,
        choices=["full", "half", "quarter", "eighth", "sixteenth", "thirtysecond"],
        default="sixteenth",
        help="Microstepping mode (default: sixteenth)",
    )

    # Movement options (mutually exclusive groups)
    movement = parser.add_mutually_exclusive_group()

    movement.add_argument(
        "--degrees", "-d",
        type=float,
        help="Degrees to rotate (negative for counter-clockwise)",
    )

    movement.add_argument(
        "--steps",
        type=int,
        help="Number of steps to move (direct control)",
    )

    movement.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Continuous rotation (Ctrl+C to stop)",
    )

    parser.add_argument(
        "--rpm", "-r",
        type=float,
        default=60,
        help="Rotations per minute (default: 60)",
    )

    parser.add_argument(
        "--direction",
        type=str,
        choices=["cw", "ccw"],
        default="cw",
        help="Direction (default: cw)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.001,
        help="Delay between steps in seconds (for --steps mode, default: 0.001)",
    )

    parser.add_argument(
        "--duration", "-t",
        type=float,
        help="Duration in seconds (for --continuous mode)",
    )

    args = parser.parse_args()

    # Map microstep string to enum
    microstep_map = {
        "full": MicrostepMode.FULL,
        "half": MicrostepMode.HALF,
        "quarter": MicrostepMode.QUARTER,
        "eighth": MicrostepMode.EIGHTH,
        "sixteenth": MicrostepMode.SIXTEENTH,
        "thirtysecond": MicrostepMode.THIRTYSECOND,
    }

    try:
        with StepperMotor(
            motor=args.motor,
            steps_per_rev=args.steps_per_rev,
            microstep_mode=microstep_map[args.microstep],
        ) as motor:
            print(f"Motor {args.motor} initialized")
            print(f"  Steps per rev: {motor.steps_per_rev}")
            print(f"  Microstep mode: {args.microstep} ({motor.microstep_multiplier}x)")
            print(f"  Effective steps/rev: {motor.effective_steps_per_rev}")
            print()

            if args.continuous:
                print(f"Continuous rotation at {args.rpm} RPM ({args.direction})")
                print("Press Ctrl+C to stop...")
                motor.rotate_continuous(
                    rpm=args.rpm,
                    direction=args.direction,
                    duration=args.duration,
                )
            elif args.steps:
                print(f"Moving {args.steps} steps ({args.direction})")
                motor.step(args.steps, args.direction, args.delay)
            elif args.degrees:
                direction = args.direction
                degrees = args.degrees
                if degrees < 0:
                    direction = "ccw" if args.direction == "cw" else "cw"
                    degrees = abs(degrees)
                print(f"Rotating {degrees}° {direction} at {args.rpm} RPM")
                motor.rotate(degrees=degrees, rpm=args.rpm, direction=direction)
            else:
                # Default: one full rotation
                print(f"Rotating 360° {args.direction} at {args.rpm} RPM")
                motor.rotate(degrees=360, rpm=args.rpm, direction=args.direction)

            print("Done!")

    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
