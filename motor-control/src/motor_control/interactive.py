"""Interactive motor control interface."""

import sys
import time
import threading
from .stepper import StepperMotor, MicrostepMode


class MotorController:
    """Interactive controller for stepper motor."""

    def __init__(self):
        self.motor = None
        self.running = False
        self.direction = "cw"
        self.rpm = 60
        self.motor_num = 1
        self.microstep = MicrostepMode.SIXTEENTH
        self._stop_flag = False
        self._run_thread = None

    @property
    def gpio_claimed(self):
        """Check if GPIO is currently claimed."""
        return self.motor is not None

    def on(self):
        """Claim GPIO and enable motor driver."""
        if self.motor:
            print("Already on. Use 'off' first to release GPIO.")
            return
        self.motor = StepperMotor(
            motor=self.motor_num,
            steps_per_rev=200,
            microstep_mode=self.microstep,
        )
        self.motor.enable()
        print(f"Motor {self.motor_num} ON (GPIO claimed, driver enabled)")
        print(f"  Effective steps/rev: {self.motor.effective_steps_per_rev}")

    def off(self):
        """Stop rotation, disable driver, and release GPIO."""
        self.stop()
        if self.motor:
            self.motor.cleanup()
            self.motor = None
            print("Motor OFF (driver disabled, GPIO released)")
        else:
            print("Motor already off")

    def start_continuous(self):
        """Start continuous rotation in background."""
        if not self.motor:
            print("Motor is off. Use 'on' first.")
            return
        if self.running:
            print("Already running! Use 'stop' first.")
            return
        self._stop_flag = False
        self.running = True

        def run():
            rps = self.rpm / 60
            steps_per_second = rps * self.motor.effective_steps_per_rev
            delay = 1 / steps_per_second if steps_per_second > 0 else 0.001
            min_pulse = 0.000002  # 2μs minimum pulse width

            import lgpio
            dir_value = 1 if self.direction == "cw" else 0
            lgpio.gpio_write(self.motor._chip, self.motor._pins["dir"], dir_value)
            time.sleep(0.000005)

            step_pin = self.motor._pins["step"]
            next_time = time.perf_counter()

            while not self._stop_flag:
                lgpio.gpio_write(self.motor._chip, step_pin, 1)
                pulse_end = time.perf_counter() + min_pulse
                while time.perf_counter() < pulse_end:
                    pass
                lgpio.gpio_write(self.motor._chip, step_pin, 0)

                next_time += delay
                wait_time = next_time - time.perf_counter()
                if wait_time > 0.001:
                    time.sleep(wait_time - 0.0005)
                while time.perf_counter() < next_time:
                    pass

            self.running = False

        self._run_thread = threading.Thread(target=run, daemon=True)
        self._run_thread.start()
        print(f"Started: {self.rpm} RPM, direction: {self.direction}")

    def stop(self):
        """Stop continuous rotation."""
        if self.running:
            self._stop_flag = True
            if self._run_thread:
                self._run_thread.join(timeout=1)
            self.running = False
            print("Stopped")

    def rotate_degrees(self, degrees):
        """Rotate specific degrees."""
        if not self.motor:
            print("Motor is off. Use 'on' first.")
            return
        print(f"Rotating {degrees}° {self.direction} at {self.rpm} RPM...")
        self.motor.rotate(degrees=degrees, rpm=self.rpm, direction=self.direction)
        print("Done")

    def rotate_time(self, seconds):
        """Rotate for specific time."""
        if not self.motor:
            print("Motor is off. Use 'on' first.")
            return
        print(f"Rotating for {seconds}s {self.direction} at {self.rpm} RPM...")
        self.motor.rotate_continuous(rpm=self.rpm, direction=self.direction, duration=seconds)
        print("Done")

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if self.motor:
            self.motor.cleanup()
            self.motor = None


def print_help():
    """Print available commands."""
    print("""
Commands:
  on        - Claim GPIO and enable motor driver
  off       - Disable driver and release GPIO
  start     - Start continuous rotation (requires 'on')
  stop      - Stop rotation (keeps motor enabled)

  cw        - Set direction clockwise
  ccw       - Set direction counter-clockwise

  rpm N     - Set speed to N RPM (e.g., 'rpm 120')
  deg N     - Rotate N degrees (e.g., 'deg 360')
  time N    - Rotate for N seconds (e.g., 'time 5')

  motor N   - Switch to motor N (1 or 2), releases GPIO
  micro M   - Set microstep mode, releases GPIO
              (full/half/quarter/eighth/sixteenth/thirtysecond)

  status    - Show current settings
  help      - Show this help
  quit      - Exit
""")


def print_status(ctrl):
    """Print current status."""
    gpio_status = "CLAIMED" if ctrl.gpio_claimed else "released"
    enabled_status = ctrl.motor._enabled if ctrl.motor else False
    print(f"""
Current Settings:
  Motor:      {ctrl.motor_num}
  GPIO:       {gpio_status}
  Enabled:    {enabled_status}
  Running:    {ctrl.running}
  Direction:  {ctrl.direction}
  Speed:      {ctrl.rpm} RPM
  Microstep:  {ctrl.microstep.name}
""")


def main():
    """Main interactive loop."""
    print("=" * 50)
    print("  Stepper Motor Interactive Control")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit")
    print()

    ctrl = MotorController()

    microstep_map = {
        "full": MicrostepMode.FULL,
        "half": MicrostepMode.HALF,
        "quarter": MicrostepMode.QUARTER,
        "eighth": MicrostepMode.EIGHTH,
        "sixteenth": MicrostepMode.SIXTEENTH,
        "thirtysecond": MicrostepMode.THIRTYSECOND,
    }

    try:
        while True:
            try:
                state = "ON" if ctrl.gpio_claimed else "off"
                run_state = " RUN" if ctrl.running else ""
                cmd = input(f"[{state}{run_state} {ctrl.direction} {ctrl.rpm}rpm] > ").strip().lower()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0]

            try:
                if action == "quit" or action == "q" or action == "exit":
                    break
                elif action == "help" or action == "h" or action == "?":
                    print_help()
                elif action == "status" or action == "s":
                    print_status(ctrl)
                elif action == "on":
                    ctrl.on()
                elif action == "off":
                    ctrl.off()
                elif action == "start":
                    ctrl.start_continuous()
                elif action == "stop":
                    ctrl.stop()
                elif action == "cw":
                    ctrl.direction = "cw"
                    print("Direction: clockwise")
                elif action == "ccw":
                    ctrl.direction = "ccw"
                    print("Direction: counter-clockwise")
                elif action == "rpm":
                    if len(parts) > 1:
                        ctrl.rpm = float(parts[1])
                        print(f"Speed: {ctrl.rpm} RPM")
                    else:
                        print(f"Current speed: {ctrl.rpm} RPM")
                elif action == "deg":
                    if len(parts) > 1:
                        ctrl.rotate_degrees(float(parts[1]))
                    else:
                        print("Usage: deg <degrees>")
                elif action == "time":
                    if len(parts) > 1:
                        ctrl.rotate_time(float(parts[1]))
                    else:
                        print("Usage: time <seconds>")
                elif action == "motor":
                    if len(parts) > 1 and parts[1] in ("1", "2"):
                        new_motor = int(parts[1])
                        if ctrl.motor:
                            ctrl.off()  # Release GPIO before switching
                        ctrl.motor_num = new_motor
                        print(f"Switched to motor {ctrl.motor_num} (use 'on' to claim GPIO)")
                    else:
                        print("Usage: motor <1|2>")
                elif action == "micro":
                    if len(parts) > 1 and parts[1] in microstep_map:
                        if ctrl.motor:
                            ctrl.off()  # Release GPIO before changing mode
                        ctrl.microstep = microstep_map[parts[1]]
                        print(f"Microstep: {ctrl.microstep.name} (use 'on' to apply)")
                    else:
                        print(f"Usage: micro <{'/'.join(microstep_map.keys())}>")
                else:
                    print(f"Unknown command: {action}. Type 'help' for commands.")
            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        print("Cleaning up...")
        ctrl.cleanup()
        print("Bye!")


if __name__ == "__main__":
    main()
