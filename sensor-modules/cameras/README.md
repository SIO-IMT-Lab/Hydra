# Cameras

Drivers and utilities for Hydra's camera systems.

Currently three FLIR based cameras are supported:

* **BubbleCam** – captures bursts of images around wave-breaking events
  triggered by the conductivity system.
* **FoamCam** – identical hardware and behaviour to BubbleCam but stores foam
  imagery using its own configuration.
* **WhiteCapCam** – periodically samples whitecaps at a fixed interval while
  the glider is active.

Shared functionality lives in ``sensor-modules/cameras/common``.

## Usage

Each camera module is self-contained:

1. ``cd`` into the camera's directory, for example:

   ```bash
   cd sensor-modules/cameras/bubblecam
   python main.py
   ```

2. The camera starts using the parameters defined in its ``config.py`` file.

## Configuration

Every camera directory includes a ``config.py`` file. Edit it to adjust:

* **Image storage** (``IMG_DIR``, ``IMG_TYPE``)
* **Camera settings** (``EXPOSURE``, ``GAIN``, ``BRIGHTNESS``, ``FPS``, etc.)
* **Device selection** (``CAMERA_ID`` – index, serial number or device path)
* **Module specifics** (``ROLL_BUF_SIZE``, ``EVENT_DELAY``,
  ``CAPTURE_INTERVAL``, etc.)
* **Networking and logging** (``SERVER_IP``, ``SERVER_PORT``, ``LOG_FILE``, ...)

Update the values to suit your deployment before running the camera.

## Camera Selection

Each camera's configuration file defines a ``CAMERA_ID`` setting used to
select the hardware device. The identifier can be an integer index, the
camera's serial number or a device path (e.g. ``/dev/video2``). This allows
multiple cameras such as BubbleCam, FoamCam and WhiteCapCam to operate on the
same machine without conflicting over device ``0``.
