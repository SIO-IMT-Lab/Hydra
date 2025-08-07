from typing import Callable, Deque

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
            self.camera.release()

    def _open_camera(self) -> None:
        """(Re)initialize the camera with the configured parameters."""
        if SpinVideoCapture is not None:
            try:
                self.camera = SpinVideoCapture(0)
                self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
                self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
                self.camera.set(cv2.CAP_PROP_GAMMA, self.gamma)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)
                return
            except Exception:
                pass
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.camera.set(cv2.CAP_PROP_GAMMA, self.gamma)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)

    def reset(self) -> None:
        """Reset the camera connection."""
        self.power_off()
        time.sleep(0.5)
        self._open_camera()
