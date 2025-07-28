from typing import Callable, Deque

import cv2

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

        # Initialize the video capture device immediately.  Prefer the FLIR
        # ``EasyPySpin`` backend when available since BubbleCam uses a Spinnaker
        # compatible camera.  If that backend cannot be used (e.g. the
        # proprietary ``PySpin`` bindings are not installed) we fall back to the
        # standard OpenCV ``VideoCapture`` implementation.  ``isOpened`` can be
        # checked by callers if needed.
        if SpinVideoCapture is not None:
            try:
                self.camera = SpinVideoCapture(0)
            except Exception:
                self.camera = cv2.VideoCapture(0)
        else:
            self.camera = cv2.VideoCapture(0)

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
