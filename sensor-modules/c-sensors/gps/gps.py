"""Simple GPS logger used on the Hydra platform.

This module reads NMEA sentences from a USB GPS receiver and logs `$GPRMC`
messages to a dated text file.  It also listens for a 1&nbsp;PPS signal on a GPIO
pin and records the rising edge times in the same file.  The script was
originally written for a Raspberry Pi but can be adapted for other devices.
"""

from __future__ import annotations

import argparse
import datetime as dt
import signal
import sys
from pathlib import Path

import RPi.GPIO as GPIO  # type: ignore
import serial


DEFAULT_DATA_DIR = Path("/home/pi/Desktop/IMT/gps_timestamps")
DEFAULT_GPIO_PIN = 16
DEFAULT_SERIAL_PORT = "/dev/ttyACM0"
DEFAULT_BAUDRATE = 9600


def parse_args() -> argparse.Namespace:
    """Return command line arguments."""
    parser = argparse.ArgumentParser(description="Hydra GPS logger")
    parser.add_argument(
        "--port",
        default=DEFAULT_SERIAL_PORT,
        help="Serial device path for the GPS",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="Serial port baudrate",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory where log files will be written",
    )
    parser.add_argument(
        "--gpio-pin",
        type=int,
        default=DEFAULT_GPIO_PIN,
        help="GPIO pin used for the 1PPS signal",
    )
    return parser.parse_args()

def init_log_file(data_dir: Path) -> Path:
    """Return the path to today's log file inside *data_dir*.

    The directory is created if it does not already exist.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    date_str = dt.datetime.now().date().isoformat()
    return data_dir / f"{date_str}.txt"

# ser is open serial port
# log_file is open file to write data to
# data is like a string buffer, only write to file when whole string is built since write ops are slow!!
def process_uart_char(ser: serial.Serial, log_file, buffer: str) -> str:
    """Read a single character and update *buffer*.

    Completed `$GPRMC` sentences are appended to *log_file*.
    """
    char = ser.read().decode(errors="ignore")
    if char == "\n":
        buffer += char
        if "$GPRMC" in buffer:
            log_file.write(buffer)
            log_file.flush()
        return ""
    else:
        return buffer + char

def one_pps_callback(log_file):
    """Return a callback that logs 1PPS rising edges to *log_file*."""

    def _cb(channel: int) -> None:
        curr_time = dt.datetime.now().isoformat()
        log_file.write(f"Rising Edge @ {curr_time}\n")
        log_file.flush()

    return _cb

def gpio_setup(pin: int, log_file) -> None:
    """Configure GPIO for the 1PPS interrupt."""

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=one_pps_callback(log_file))

def signal_handler(log_file):
    """Return a SIGINT handler that cleans up resources."""

    def _handler(sig, frame):
        print("ending.........")
        try:
            log_file.close()
        finally:
            GPIO.cleanup()
        sys.exit(0)

    return _handler


def main() -> None:
    args = parse_args()
    log_path = init_log_file(args.data_dir)

    with serial.Serial(args.port, baudrate=args.baudrate) as ser, open(
        log_path, "w"
    ) as log_file:
        gpio_setup(args.gpio_pin, log_file)
        signal.signal(signal.SIGINT, signal_handler(log_file))

        log_file.write("Hello World!\n\n")
        buffer = ""
        while True:
            buffer = process_uart_char(ser, log_file, buffer)


if __name__ == "__main__":
    main()
