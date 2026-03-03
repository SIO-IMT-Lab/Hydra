"""Tkinter GUI for controlling MCP23017 A and B pins."""

import argparse
import tkinter as tk
from tkinter import ttk
import board
import busio
import digitalio
from adafruit_mcp230xx.mcp23017 import MCP23017


def run_gui(address: int) -> None:
    """Launch a GUI to toggle MCP23017 pins."""

    i2c = busio.I2C(board.SCL, board.SDA)
    mcp = MCP23017(i2c, address=address)

    a_pins: list[digitalio.DigitalInOut] = []
    b_pins: list[digitalio.DigitalInOut] = []
    for pin_num in range(8):
        a_pin = mcp.get_pin(pin_num)
        b_pin = mcp.get_pin(pin_num + 8)
        a_pin.direction = digitalio.Direction.OUTPUT
        b_pin.direction = digitalio.Direction.OUTPUT
        a_pin.value = False
        b_pin.value = False
        a_pins.append(a_pin)
        b_pins.append(b_pin)

    root = tk.Tk()
    root.title("MCP23017 A & B Pins Controller")
    root.geometry("600x500")
    root.configure(bg="#2c3e50")

    header = tk.Label(
        root,
        text="MCP23017 A0–A7 and B0–B7 Control Panel",
        font=("Arial", 18, "bold"),
        bg="#2c3e50",
        fg="white",
    )
    header.pack(pady=10)

    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack()

    a_indicators: list[tk.Label] = []
    b_indicators: list[tk.Label] = []

    def update_indicators() -> None:
        for i, pin in enumerate(a_pins):
            a_indicators[i].config(bg="green" if pin.value else "red")
        for i, pin in enumerate(b_pins):
            b_indicators[i].config(bg="green" if pin.value else "red")

    def toggle_pin(pins: list[digitalio.DigitalInOut], idx: int) -> None:
        pins[idx].value = not pins[idx].value
        update_indicators()

    def set_pin(pins: list[digitalio.DigitalInOut], idx: int, state: bool) -> None:
        pins[idx].value = state
        update_indicators()

    def show_status() -> None:
        status_lines = []
        status_lines += [f"A{i}: {'HIGH' if p.value else 'LOW'}" for i, p in enumerate(a_pins)]
        status_lines += [f"B{i}: {'HIGH' if p.value else 'LOW'}" for i, p in enumerate(b_pins)]
        status_window = tk.Toplevel(root)
        status_window.title("Pin Status")
        tk.Label(
            status_window,
            text="\n".join(status_lines),
            font=("Courier", 12),
            justify="left",
        ).pack(padx=20, pady=20)

    def create_pin_controls(
        frame: ttk.Frame,
        label_prefix: str,
        pins: list[digitalio.DigitalInOut],
        indicators: list[tk.Label],
    ) -> None:
        section = ttk.LabelFrame(frame, text=f"{label_prefix} Pins", padding=10)
        section.pack(side="left", padx=10)

        for i in range(8):
            row = ttk.Frame(section, padding=5)
            row.pack(anchor="w")

            label = ttk.Label(row, text=f"{label_prefix}{i}", width=4)
            label.pack(side="left")

            indicator = tk.Label(row, text=" ", bg="red", width=2, height=1, relief="groove")
            indicator.pack(side="left", padx=5)
            indicators.append(indicator)

            ttk.Button(row, text="Toggle", command=lambda i=i: toggle_pin(pins, i)).pack(side="left", padx=2)
            ttk.Button(row, text="ON", command=lambda i=i: set_pin(pins, i, True)).pack(side="left", padx=2)
            ttk.Button(row, text="OFF", command=lambda i=i: set_pin(pins, i, False)).pack(side="left", padx=2)

    create_pin_controls(main_frame, "A", a_pins, a_indicators)
    create_pin_controls(main_frame, "B", b_pins, b_indicators)

    bottom_frame = ttk.Frame(root, padding=10)
    bottom_frame.pack()

    ttk.Button(bottom_frame, text="Show Status", command=show_status).pack(side="left", padx=10)
    ttk.Button(bottom_frame, text="Exit", command=root.quit).pack(side="left", padx=10)

    update_indicators()
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Tkinter GUI for MCP23017 control")
    parser.add_argument(
        "--address",
        type=lambda x: int(x, 0),
        default="0x20",
        help="I2C address of the MCP23017 (default: 0x20)",
    )
    args = parser.parse_args()
    run_gui(args.address)


if __name__ == "__main__":
    main()
