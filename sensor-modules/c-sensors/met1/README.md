# MET1 Module (Air Particle Counter)

Code for interfacing with the MET1 air particle counter. The sensor is
controlled by a Feather microcontroller while a Python script running on
the host computer logs the serial output.

Hydra samples the MET1 every 30 minutes unless the platform enters
**LOCKDOWN** due to high winds. Communication with the device happens
through the Feather over UART.

## Files

- `apc_controller.ino` – Arduino sketch for the Feather board. It
  controls the pumps and valves and monitors two seawater switches.
  Configuration options such as pin numbers and thresholds are declared
  at the top of the file so they can be changed easily.
- `met1_logger.py` – Python script that reads lines from the MET1 over a
  serial connection and appends them to a CSV file with timestamps.

## Running the Python logger

Connect the MET1 serial output to your machine and execute:

```bash
python met1_logger.py --port /dev/ttyUSB2 --output met1_data.csv
```

Optional flags allow you to modify the serial baud rate, timeout and the
output file location.

The script writes each received line together with the current UTC time
to the specified CSV file.

## Uploading the microcontroller code

Open `apc_controller.ino` in the Arduino IDE or PlatformIO and upload it
to the Feather board. If your hardware uses different pins or you need
a different seawater switch threshold, adjust the constants at the top
of the sketch before uploading.
