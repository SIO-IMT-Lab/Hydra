# Cameras

Drivers and utilities for Hydra's camera systems.

Currently two FLIR based cameras are supported:

* **BubbleCam** – the original camera module.
* **FoamCam** – a second camera sharing the same implementation but with its
  own configuration.

Shared functionality lives in ``sensor-modules/cameras/common``.

## Camera Selection

Each camera's configuration file now defines a ``CAMERA_ID`` setting used to
select the hardware device.  The identifier can be either an integer index,
the camera's serial number or a device path (e.g. ``/dev/video2``).  This
allows multiple cameras such as BubbleCam and FoamCam to operate on the same
machine without conflicting over device ``0``.