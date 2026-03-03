"""Interactive CLI for controlling MCP23017 GPIO pins."""

import argparse
import board
import busio
import digitalio

from adafruit_mcp230xx.mcp23017 import MCP23017


def get_pin_index(name: str) -> int | None:
    """Return the numeric index for an A-pin name (e.g. 'A0')."""

    if name.upper().startswith("A"):
        idx = int(name[1:])
        if 0 <= idx <= 7:
            return idx
    return None


def run_cli(address: int) -> None:
    """Start an interactive shell for MCP23017 pin control."""

    i2c = busio.I2C(board.SCL, board.SDA)
    mcp = MCP23017(i2c, address=address)

    pins = []
    for pin_num in range(8):
        pin = mcp.get_pin(pin_num)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False
        pins.append(pin)

    print("MCP23017 A pins (A0–A7) set as outputs.")
    print("Type commands like: set A0 on, set A3 off, toggle A2, status, exit")

    try:
        while True:
            command = input(">>> ").strip().lower()
            if command == "exit":
                print("Exiting...")
                break
            elif command == "status":
                for i, pin in enumerate(pins):
                    print(f"A{i}: {'HIGH' if pin.value else 'LOW'}")
            elif command.startswith("set "):
                parts = command.split()
                if len(parts) == 3:
                    pin_name, state = parts[1], parts[2]
                    idx = get_pin_index(pin_name)
                    if idx is not None and state in ["on", "off"]:
                        pins[idx].value = state == "on"
                        print(f"Set A{idx} {'HIGH' if pins[idx].value else 'LOW'}")
                    else:
                        print("Invalid command. Example: set A0 on")
                else:
                    print("Invalid command format. Example: set A0 on")
            elif command.startswith("toggle "):
                parts = command.split()
                if len(parts) == 2:
                    pin_name = parts[1]
                    idx = get_pin_index(pin_name)
                    if idx is not None:
                        pins[idx].value = not pins[idx].value
                        print(f"Toggled A{idx} to {'HIGH' if pins[idx].value else 'LOW'}")
                    else:
                        print("Invalid pin. Example: toggle A2")
                else:
                    print("Invalid command format. Example: toggle A2")
            else:
                print("Unknown command. Available: set, toggle, status, exit")
    except KeyboardInterrupt:
        print("\nExiting cleanly...")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive MCP23017 GPIO controller")
    parser.add_argument(
        "--address",
        type=lambda x: int(x, 0),
        default="0x20",
        help="I2C address of the MCP23017 (default: 0x20)",
    )
    args = parser.parse_args()
    run_cli(args.address)


if __name__ == "__main__":
    main()
