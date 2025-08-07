from common.camera import Camera
import config


class BubbleCam(Camera):
    """Bubble Cam implementation using the shared camera framework."""

    def __init__(self) -> None:
        super().__init__("bubblecam", config)
