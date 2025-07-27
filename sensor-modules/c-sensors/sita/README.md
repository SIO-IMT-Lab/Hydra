# SITA Water Sampler

This directory contains a small logger for the SITA surface tension
instrument used on the Hydra platform.  Measurements are taken over a
serial connection and appended to a text file with timestamps.

## Running the logger

The logger is implemented in `sita.py` and can be executed directly:

```bash
python sita.py --port /dev/ttyUSB4 --baudrate 57600 --output sita_log.txt
```

All command line arguments are optional.  The most common options are:

- `--port` – serial device where the SITA is connected
- `--baudrate` – serial baudrate (default `57600`)
- `--interval` – seconds between measurements (default `1800`)
- `--output` – file where results will be appended
- `--measure-time-limit` – maximum seconds to wait for a response

The script powers on the sampler, waits for a reading and powers it
down again.  Each line written to the output file begins with a UTC
timestamp followed by the raw response from the device.  If the timeout
is reached before a response is received, a timeout message is logged
instead.

Press <kbd>Ctrl+C</kbd> to stop the logger gracefully.