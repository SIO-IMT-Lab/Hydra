# GPS Module

Interface code for the Hydra GPS receiver. The hardware originates from the Liquid Robotics sensor suite, but the logic here is tailored for Hydra.

The module parses NMEA messages from the device and also handles the 1 PPS signal used for precise time synchronization.

## Usage

The logger requires a serial-connected GPS and a GPIO pin providing the
1 pulse‑per‑second (1&nbsp;PPS) signal.  The script creates a dated log file in the
specified directory containing `$GPRMC` sentences and timestamps for each rising
edge on the PPS pin.

```bash
python gps.py [--port /dev/ttyUSB0] [--baudrate 9600] \
    [--data-dir /path/to/logs] [--gpio-pin 16]
```

All arguments are optional and default to the values shown above.  Interrupt the
program with <kbd>Ctrl+C</kbd> to close the log file and clean up GPIO state.
