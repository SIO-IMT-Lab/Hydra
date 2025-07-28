from collections import deque
from typing import Callable, Deque, Optional

import cv2


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
        # In a real deployment this would be cv2.VideoCapture(0)
        self.camera: Optional[cv2.VideoCapture] = None

    def start_workflow(self, buffer: Deque, lock) -> None:
        """Start capturing images using ``capture_function``."""
        self.capture_function(buffer, lock)

    def capture_image(self):
        """Capture a single frame (stubbed for tests)."""
        if self.camera is None:
            return True, None
        return self.camera.read()

    def power_off(self) -> None:
        """Release the camera handle."""
        if self.camera is not None:
            self.camera.release()
