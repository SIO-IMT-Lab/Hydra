"""Command line interface for reading ADS1015 voltages."""

import argparse
import time
import board
import busio

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn


def read_ads(addresses: list[int], ratio: float, interval: float) -> None:
    """Continuously print readings from ADS1015 devices.

    Parameters
    ----------
    addresses: list[int]
        List of I2C addresses for ADS1015 devices.
    ratio: float
        Scaling factor applied to each voltage reading.
    interval: float
        Delay between consecutive readings in seconds.
    """

    i2c = busio.I2C(board.SCL, board.SDA)
    devices = [ADS1015(i2c, address=addr) for addr in addresses]
    channels = [[AnalogIn(dev, ch) for ch in range(4)] for dev in devices]

    try:
        while True:
            for dev_idx, ch_list in enumerate(channels):
                addr = addresses[dev_idx]
                print(f"ADS1015 #{dev_idx + 1} (0x{addr:02x}) readings:")
                for ch_idx, ch in enumerate(ch_list):
                    voltage = ch.voltage * ratio
                    print(f"  Channel {ch_idx}: {voltage:.3f} V")
            print(f"\n--- Waiting {interval} second(s) ---\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nExiting cleanly...")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read scaled voltages from ADS1015 devices")
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
        help="Delay between readings in seconds (default: 1.0)",
    )

    args = parser.parse_args()
    addresses = [int(addr, 0) for addr in args.addresses]
    read_ads(addresses, args.ratio, args.interval)


if __name__ == "__main__":
    main()
