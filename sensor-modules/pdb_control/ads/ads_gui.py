"""Tkinter GUI for live ADS1015 readings."""

import argparse
import time
import threading
import board
import busio
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn


def run_gui(addresses: list[int], ratio: float, interval: float) -> None:
    """Launch a GUI showing live voltages from ADS1015 devices."""

    i2c = busio.I2C(board.SCL, board.SDA)
    devices = [ADS1015(i2c, address=addr) for addr in addresses]
    channels = [[AnalogIn(dev, ch) for ch in range(4)] for dev in devices]
    data = [0.0] * (4 * len(devices))

    def update_data() -> None:
        while True:
            for dev_idx, ch_list in enumerate(channels):
                for ch_idx, ch in enumerate(ch_list):
                    data[dev_idx * 4 + ch_idx] = ch.voltage * ratio
            time.sleep(interval)

    threading.Thread(target=update_data, daemon=True).start()

    root = tk.Tk()
    root.title("Live ADS1015 Readings")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    labels = []
    for i in range(len(data)):
        label = ttk.Label(frame, text=f"Channel {i}: --- V", font=("Arial", 14))
        label.grid(row=i, column=0, sticky=tk.W)
        labels.append(label)

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    bars = ax.bar(range(len(data)), data)
    ax.set_ylim(0, 30)
    ax.set_ylabel("Voltage (V)")
    ax.set_title("Scaled ADS1015 Voltages")
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels([f"Ch {i}" for i in range(len(data))])

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1, rowspan=len(data))

    def refresh_gui() -> None:
        for i, label in enumerate(labels):
            label.config(text=f"Channel {i}: {data[i]:.2f} V")
            bars[i].set_height(data[i])
        canvas.draw()
        root.after(int(interval * 1000), refresh_gui)

    root.after(int(interval * 1000), refresh_gui)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live ADS1015 readings in a Tkinter GUI")
    parser.add_argument(
        "--addresses",
        nargs="+",
        default=["0x48", "0x49", "0x4A", "0x4B"],
        help="I2C addresses of ADS1015 chips (default: 0x48 0x49 0x4A 0x4B)",
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
    addresses = [int(addr, 0) for addr in args.addresses]
    run_gui(addresses, args.ratio, args.interval)


if __name__ == "__main__":
    main()
