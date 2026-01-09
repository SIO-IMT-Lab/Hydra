"""Combined ADS1015 and MCP23017 GUI with configurable options."""

import argparse
import csv
import threading
import time
from pathlib import Path
from typing import Optional

import board
import busio
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio


def load_channel_metadata(csv_path: Path) -> tuple[dict[int, str], dict[str, int]]:
    """Load channel and control pin names from a CSV file."""

    channel_names: dict[int, str] = {}
    pin_channels: dict[str, int] = {}

    try:
        with csv_path.open(newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            for row in reader:
                if not row or not any(cell.strip() for cell in row):
                    continue

                name = row[0].strip()

                channel_idx: Optional[int] = None
                if len(row) > 7:
                    try:
                        channel_idx = int(row[7], 0)
                    except ValueError:
                        channel_idx = None

                pin_label = ""
                if len(row) > 8:
                    pin_label = row[8].strip().upper()

                if channel_idx is not None and 0 <= channel_idx < 64 and name:
                    channel_names[channel_idx] = name

                if (
                    channel_idx is not None
                    and pin_label
                    and pin_label[0] in {"A", "B"}
                ):
                    pin_channels[pin_label] = channel_idx

    except FileNotFoundError:
        pass

    return channel_names, pin_channels


def run_gui(ads_addresses: list[int], mcp_address: int, ratio: float, interval: float) -> None:
    """Launch the combined ADS1015/MCP23017 GUI."""

    csv_path = Path(__file__).with_name("data.csv")
    channel_name_map, pin_channel_map = load_channel_metadata(csv_path)

    i2c = busio.I2C(board.SCL, board.SDA)
    ads_devices = [ADS1015(i2c, address=a) for a in ads_addresses]
    ads_channels = [[AnalogIn(dev, ch) for ch in range(4)] for dev in ads_devices]
    data = [0.0] * (4 * len(ads_devices))

    channel_labels = [
        channel_name_map.get(idx, f"Channel {idx}") for idx in range(len(data))
    ]

    mcp = MCP23017(i2c, address=mcp_address)
    a_pins: list[digitalio.DigitalInOut] = []
    b_pins: list[digitalio.DigitalInOut] = []
    for pin_num in range(8):
        a = mcp.get_pin(pin_num)
        b = mcp.get_pin(pin_num + 8)
        a.direction = digitalio.Direction.OUTPUT
        b.direction = digitalio.Direction.OUTPUT
        a.value = False
        b.value = False
        a_pins.append(a)
        b_pins.append(b)

    def update_data() -> None:
        while True:
            for dev_idx, ch_list in enumerate(ads_channels):
                for ch_idx, ch in enumerate(ch_list):
                    data[dev_idx * 4 + ch_idx] = ch.voltage * ratio
            time.sleep(interval)

    threading.Thread(target=update_data, daemon=True).start()

    root = tk.Tk()
    root.title("ADS1015 + MCP23017 GUI")

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0)

    ads_frame = ttk.Frame(main_frame, padding=10)
    ads_frame.grid(row=0, column=0)

    mcp_frame = ttk.Frame(main_frame, padding=10)
    mcp_frame.grid(row=0, column=1)

    ads_labels: list[ttk.Label] = []
    for i, channel_name in enumerate(channel_labels):
        label = ttk.Label(ads_frame, text=f"{channel_name}: --- V", font=("Arial", 12))
        label.grid(row=i, column=0, sticky=tk.W)
        ads_labels.append(label)

    fig_width = max(6, 0.6 * len(data))
    fig = Figure(figsize=(fig_width, 3), dpi=100)
    ax = fig.add_subplot(111)
    bars = ax.bar(range(len(data)), data)
    ax.set_ylim(0, 30)
    ax.set_ylabel("Voltage (V)")
    ax.set_title("ADS1015 Voltages")
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(channel_labels)
    ax.tick_params(axis="x", labelrotation=45)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=ads_frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1, rowspan=len(data))

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

    def create_pin_controls(
        frame: ttk.Frame,
        label_prefix: str,
        pins: list[digitalio.DigitalInOut],
        indicators: list[tk.Label],
        pin_labels: list[str],
    ) -> None:
        section = ttk.LabelFrame(frame, text=f"{label_prefix} Pins", padding=5)
        section.pack(padx=5, pady=5)
        for i, label_text in enumerate(pin_labels):
            row = ttk.Frame(section)
            row.pack(anchor="w")
            ttk.Label(row, text=label_text).pack(side="left")
            ind = tk.Label(row, text=" ", bg="red", width=2, height=1, relief="groove")
            ind.pack(side="left", padx=5)
            indicators.append(ind)
            ttk.Button(row, text="Toggle", command=lambda i=i: toggle_pin(pins, i)).pack(side="left")
            ttk.Button(row, text="ON", command=lambda i=i: set_pin(pins, i, True)).pack(side="left")
            ttk.Button(row, text="OFF", command=lambda i=i: set_pin(pins, i, False)).pack(side="left")

    def build_pin_labels(prefix: str) -> list[str]:
        labels: list[str] = []
        for idx in range(8):
            pin_id = f"{prefix}{idx}"
            channel_idx = pin_channel_map.get(pin_id.upper())
            if channel_idx is not None and 0 <= channel_idx < len(channel_labels):
                channel_name = channel_labels[channel_idx]
                labels.append(f"{pin_id} - {channel_name}")
            else:
                labels.append(pin_id)
        return labels

    create_pin_controls(mcp_frame, "A", a_pins, a_indicators, build_pin_labels("A"))
    create_pin_controls(mcp_frame, "B", b_pins, b_indicators, build_pin_labels("B"))

    def refresh_gui() -> None:
        for i, label in enumerate(ads_labels):
            label.config(text=f"{channel_labels[i]}: {data[i]:.2f} V")
            bars[i].set_height(data[i])
        canvas.draw()
        update_indicators()
        root.after(int(interval * 1000), refresh_gui)

    root.after(int(interval * 1000), refresh_gui)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Combined ADS1015/MCP23017 GUI")
    parser.add_argument(
        "--ads-addresses",
        nargs="+",
        default=["0x48", "0x49", "0x4A"], 
        help="I2C addresses of ADS1015 chips (default: 0x48 0x49 0x4A 0x4B)",
    )
    parser.add_argument(
        "--mcp-address",
        type=lambda x: int(x, 0),
        default="0x20",
        help="I2C address of MCP23017 (default: 0x20)",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=24 / 2.17,
        help="Scaling ratio volts/volts (default: 24/2.17)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Refresh interval in seconds (default: 1.0)",
    )
    args = parser.parse_args()
    ads_addresses = [int(a, 0) for a in args.ads_addresses]
    run_gui(ads_addresses, args.mcp_address, args.ratio, args.interval)


if __name__ == "__main__":
    main()
