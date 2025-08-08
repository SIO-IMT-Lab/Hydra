# Conductivity Sensor UI

This directory contains a small PyQt6 application used to view and log data from
the conductivity sensor.  All of the code lives in a single `app.py` script that
can be run directly.

## Installation

The UI depends on `PyQt6`, `pyqtgraph` and `pyserial`.  They can be installed
with pip:

```bash
pip install pyqt6 pyqtgraph pyserial
```

## Usage

Run the application directly with Python:

```bash
python app.py
```

The window allows you to select a serial port, start/stop streaming and logging,
plot the latest samples and record timestamped notes.  Logged data are written to
a CSV file along with an accompanying `.notes.txt` file when logging is enabled.
