from typing import Deque
import datetime
import os
import time
import threading
import cv2

from sys import getsizeof

from logger import Logger
from cam import Cam
from state import State


class Camera:
    """High level interface for a FLIR camera.

    Parameters are provided via a simple configuration object ``config`` which
    exposes the same attributes as the old ``bubblecam_config`` module.  This
    allows multiple cameras to share the same implementation while differing
    only in their configuration.
    """

    def __init__(self, name: str, config) -> None:
        self.config = config
        self.logger = Logger(config, name).logger
        self.cam = Cam(
            name,
            self.capture_loop,
            config.EXPOSURE,
            config.GAIN,
            config.BRIGHTNESS,
            config.GAMMA,
            config.FPS,
            config.BACKLIGHT,
            config.EVENT_DELAY,
            config.IMG_TYPE,
            config.ROLL_BUF_SIZE,
        )
        self.glider_state = State.STORM
        self.lockout_until = 0.0

    def capture_loop(self, buffer: Deque, lock: threading.Lock) -> None:
        """Continuously capture frames while in :class:`State.STORM`."""
        index = 1
        while True:
            try:
                success, frame = self.cam.capture_image()
            except Exception as exc:
                self.logger.error(
                    "Camera error while capturing frame %d: %s", index, exc
                )
                self.cam.reset()
                time.sleep(1)
                continue

            if not success or frame is None:
                self.logger.warning(
                    "Failed to capture frame %d; resetting camera", index
                )
                self.cam.reset()
                time.sleep(1)
                continue

            if self.glider_state != State.STORM:
                continue

            with lock:
                if len(buffer) >= self.config.ROLL_BUF_SIZE:
                    buffer.popleft()
                buffer.append(frame)

            self.logger.info("Captured frame %d", index)
            index += 1

    def write_images(self, buffer: Deque, lock: threading.Lock) -> None:
        """Write buffered frames to disk."""
        dtime_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        dtime_path = os.path.join(self.config.IMG_DIR, dtime_str)
        os.makedirs(dtime_path, exist_ok=True)
        time.sleep(self.config.EVENT_DELAY)

        with lock:
            buffer_size = getsizeof(buffer)
            for idx, img in enumerate(reversed(buffer)):
                img_path = os.path.join(dtime_path, f"img_{idx}{self.config.IMG_TYPE}")
                if isinstance(img, str):
                    self.logger.warning("Invalid frame encountered at index %d; skipping save", idx)
                    continue
                cv2.imwrite(img_path, img)
                buffer_size += getsizeof(img)
            print("Total buffer size: ", buffer_size)
            buffer.clear()

        self.logger.debug("Wrote %d images to %s", idx + 1, dtime_path)
        self.lockout_until = time.time() + self.config.LOCKOUT_DELAY

    def detect_event(self, buffer: Deque[str], lock: threading.Lock) -> None:
        """Trigger an event write if not currently locked out."""
        if time.time() < self.lockout_until:
            return
        self.write_images(buffer, lock)

    def power_off(self) -> None:
        self.cam.power_off()
