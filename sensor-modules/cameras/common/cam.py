from typing import Callable, Deque, Union

import cv2
import time

try:  # EasyPySpin depends on the proprietary PySpin bindings
    from EasyPySpin import VideoCapture as SpinVideoCapture
except Exception:  # pragma: no cover - PySpin not installed
    SpinVideoCapture = None


class Cam:
    """Basic camera wrapper used by the BubbleCam workflow."""

    def __init__(
        self,
        name: str,
        capture_function: Callable,
        camera_id: Union[int, str],
        exposure: int,
        gain: int,
        brightness: int,
        gamma: float,
        fps: int,
        backlight: int,
        event_delay: int,
        image_type: str,
        buffer_size: int,
    ) -> None:
        self.name = name
        self.capture_function = capture_function
        self.camera_id = camera_id
        self.exposure = exposure
        self.gain = gain
        self.brightness = brightness
        self.gamma = gamma
        self.fps = fps
        self.backlight = backlight
        self.event_delay = event_delay
        self.image_type = image_type
        self.buffer_size = buffer_size

        self.camera = None
        self._open_camera()

    def start_workflow(self, buffer: Deque, lock) -> None:
        """Start capturing images using ``capture_function``."""
        self.capture_function(buffer, lock)

    def capture_image(self):
        """Capture a single frame from the camera."""
        if not self.camera.isOpened():
            return False, None
        return self.camera.read()

    def power_off(self) -> None:
        """Release the camera handle."""
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                # Ignore release errors so that one failing camera does not
                # impact others that might still be running.
                pass
            finally:
                self.camera = None

    def _open_camera(self) -> None:
        """(Re)initialize the camera with the configured parameters."""
        if SpinVideoCapture is not None:
            try:
                self.camera = SpinVideoCapture(self.camera_id)
                self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
                self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
                self.camera.set(cv2.CAP_PROP_GAMMA, self.gamma)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)
                return
            except Exception:
                pass
        self.camera = cv2.VideoCapture(self.camera_id)
        self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.camera.set(cv2.CAP_PROP_GAMMA, self.gamma)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)

    def reset(self) -> None:
        """Reset the camera connection."""
        # Safely power off the existing camera and attempt to reopen it.  Any
        # exceptions during shutdown are swallowed so that the caller can
        # decide how to proceed if the camera is no longer available (for
        # example, it may have been unplugged).
        self.power_off()
        time.sleep(0.5)
        try:
            self._open_camera()
        except Exception:
            # Leave ``self.camera`` as ``None`` if reinitialisation fails.
            pass
