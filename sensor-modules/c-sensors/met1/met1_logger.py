"""MET1 particle counter logger.

This script reads lines from the MET1 device over a serial
connection and appends them to a CSV file with timestamps.
Connection parameters are configurable via command line
arguments so the script can run on different hardware
without modification.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import serial

DEFAULT_PORT = "/dev/ttyUSB2"
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
DEFAULT_OUTPUT = Path("met1_data.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read MET1 data over serial")
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help="Serial port the MET1 is connected to",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="Serial port baud rate",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Serial read timeout in seconds",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV file where readings will be appended",
    )
    return parser.parse_args()


def create_serial_connection(port: str, baudrate: int, timeout: float) -> serial.Serial:
    """Return a configured :class:`serial.Serial` object."""
    return serial.Serial(port, baudrate, timeout=timeout)


def main() -> None:
    args = parse_args()

    try:
        ser = create_serial_connection(args.port, args.baudrate, args.timeout)
    except serial.SerialException as exc:
        print(f"Failed to open serial port: {exc}")
        return

    with ser, open(args.output, "a") as f:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").rstrip()
            if not line:
                continue
            timestamp = datetime.utcnow().isoformat()
            f.write(f"{timestamp},{line}\n")
            f.flush()
            print(line)


if __name__ == "__main__":
    main()
