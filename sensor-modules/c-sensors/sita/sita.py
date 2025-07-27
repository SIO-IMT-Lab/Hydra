"""SITA water sampler interface used by Hydra.

This module provides a small :class:`Sita` helper for communicating with the
SITA controller over a serial connection together with a command line tool to
log measurements on a fixed interval.
"""

from __future__ import annotations

import argparse
import datetime as dt
import time
from pathlib import Path

import serial


POWER_UP = b"\r\n:020605000100F2\r\n"
NO_CAL = b"\r\n:020601000600F1\r\n"
SAMPLE = b"\r\n:020601000B00EC\r\n"
QUERY = b"\r\n:020618000500DB\r\n"
POWER_OFF = b"\r\n:020605000000F3\r\n"
STOP = b"\r\n:020618000000E0\r\n"


class Sita:
    """Minimal helper around the serial protocol used by the SITA sampler."""

    def __init__(self, port: str, baudrate: int = 57600, timeout: float = 1.0,
                 measure_time_limit: float = 20.0) -> None:
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.measure_time_limit = measure_time_limit

    # allow use as a context manager
    def __enter__(self) -> "Sita":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self.ser.is_open:
            self.ser.close()

    def power_on(self) -> None:
        self.ser.write(POWER_UP)
        time.sleep(1)
        self.ser.write(NO_CAL)
        time.sleep(3)
        self.ser.write(SAMPLE)
        time.sleep(1)

    def power_off(self) -> None:
        self.ser.write(POWER_OFF)
        time.sleep(0.2)
        self.ser.write(STOP)
        time.sleep(0.2)

    def take_measurement(self) -> str | None:
        """Return a single measurement string or ``None`` if timed out."""
        start = time.time()
        while True:
            self.ser.write(QUERY)
            time.sleep(0.04)
            if self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if len(line) > 20:
                    return line
            if time.time() - start > self.measure_time_limit:
                return None


DEFAULT_PORT = "/dev/ttyUSB4"
DEFAULT_BAUDRATE = 57600
DEFAULT_INTERVAL = 30 * 60  # seconds
DEFAULT_OUTPUT = Path("sita_log.txt")
DEFAULT_TIMEOUT = 1.0
DEFAULT_MEASURE_LIMIT = 20.0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hydra SITA logger")
    p.add_argument("--port", default=DEFAULT_PORT, help="Serial port for SITA")
    p.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE,
                   help="Serial baudrate")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help="Serial read timeout")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                   help="Seconds between samples")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help="File to append measurements to")
    p.add_argument("--measure-time-limit", type=float,
                   default=DEFAULT_MEASURE_LIMIT,
                   help="Maximum seconds to wait for a measurement")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    with Sita(args.port, args.baudrate, args.timeout,
              args.measure_time_limit) as sita, open(args.output, "a") as f:
        try:
            while True:
                sita.power_on()
                line = sita.take_measurement()
                sita.power_off()
                timestamp = dt.datetime.utcnow().isoformat()
                if line:
                    f.write(f"{timestamp} {line}\n")
                    f.flush()
                    print(line)
                else:
                    f.write(f"{timestamp} SITA measurement timeout\n")
                    f.flush()
                    print("SITA measurement timeout")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
