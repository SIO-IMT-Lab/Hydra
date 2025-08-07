from ..common.camera import Camera
from . import config


class FoamCam(Camera):
    """Foam Cam implementation using the shared camera framework."""

    def __init__(self) -> None:
        super().__init__("foamcam", config)
