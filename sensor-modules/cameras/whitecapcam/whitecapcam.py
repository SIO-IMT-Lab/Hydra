import datetime
import sys
from pathlib import Path
import cv2

CURRENT_DIR = Path(__file__).resolve().parent
COMMON_DIR = CURRENT_DIR.parent / "common"
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(COMMON_DIR))

from cam import Cam
from logger import Logger
import config


class WhiteCapCam:
    """Simple camera interface for capturing periodic images."""

    def __init__(self) -> None:
        self.config = config
        self.logger = Logger(config, "whitecapcam").logger
        # Capture function is unused, so provide a no-op
        self.cam = Cam(
            "whitecapcam",
            lambda buffer, lock: None,
            config.CAMERA_ID,
            config.EXPOSURE,
            config.GAIN,
            config.BRIGHTNESS,
            config.GAMMA,
            config.FPS,
            config.BACKLIGHT,
            0,
            config.IMG_TYPE,
            0,
        )

    def capture(self) -> None:
        """Capture a single image and save to disk."""
        success, frame = self.cam.capture_image()
        if not success or frame is None:
            self.logger.warning("Failed to capture image")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        img_dir = Path(self.config.IMG_DIR)
        img_dir.mkdir(parents=True, exist_ok=True)
        img_path = img_dir / f"{timestamp}{self.config.IMG_TYPE}"
        cv2.imwrite(str(img_path), frame)
        self.logger.info("Captured image %s", img_path)

    def power_off(self) -> None:
        """Power off the camera."""
        self.cam.power_off()
