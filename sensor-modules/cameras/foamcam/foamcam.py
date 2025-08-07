import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
COMMON_DIR = CURRENT_DIR.parent / "common"
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(COMMON_DIR))

from camera import Camera
import config


class FoamCam(Camera):
    """Foam Cam implementation using the shared camera framework."""

    def __init__(self) -> None:
        super().__init__("foamcam", config)
