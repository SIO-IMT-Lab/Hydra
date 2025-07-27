# Conductivity Sensor UI

This directory contains a small PyQt6 application used to view and log data from
the conductivity sensor.

- `serial_reader.py` – QThread responsible for reading samples from the serial
  port.
- `mainwindow.py` – the main Qt window handling the user interface, plotting and
  logging.
- `app.py` – lightweight entry point used to launch the UI.

## Installation

The UI depends on `PyQt6`, `pyqtgraph` and `pyserial`.  They can be installed
with pip:

```bash
pip install pyqt6 pyqtgraph pyserial
```

## Usage

Run the application using Python's module syntax so that relative imports work:

```bash
python -m conductivity_sensor.app
```

The window allows you to select a serial port, start/stop streaming and logging,
plot the latest samples and record timestamped notes.  Logged data are written to
a CSV file along with an accompanying `.notes.txt` file when logging is enabled.
