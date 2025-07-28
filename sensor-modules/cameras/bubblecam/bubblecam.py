from collections import deque
from typing import Deque
import datetime
import os
import time
import threading
import cv2

from logger import Logger
from cam import Cam
from state import State
from bubblecam_config import *


class BubbleCam:
    """High level interface for the bubble camera."""

    def __init__(self) -> None:
        self.logger = Logger(True).logger
        self.cam = Cam(
            "bubblecam",
            self.capture_loop,
            EXPOSURE,
            GAIN,
            BRIGHTNESS,
            GAMMA,
            FPS,
            BACKLIGHT,
            EVENT_DELAY,
            IMG_TYPE,
            ROLL_BUF_SIZE,
        )
        self.glider_state = State.STORM
        self.lockout_until = 0.0

    def capture_loop(self, buffer: Deque, lock: threading.Lock) -> None:
        """Continuously capture frames while in :class:`State.STORM`."""
        index = 1
        while True:
            time.sleep(1)
            if self.glider_state != State.STORM:
                continue

            success, frame = self.cam.capture_image()
            if not success or frame is None:
                img = f"frame {index}"  # fallback placeholder when no camera
            else:
                img = frame

            with lock:
                if len(buffer) >= ROLL_BUF_SIZE:
                    buffer.popleft()
                buffer.append(img)

            self.logger.info("Captured frame %d", index)
            index += 1

    def write_images(self, buffer: Deque, lock: threading.Lock) -> None:
        """Write buffered frames to disk."""
        dtime_str = datetime.datetime.now().isoformat()
        dtime_path = os.path.join(IMG_DIR, dtime_str)
        os.makedirs(dtime_path, exist_ok=True)
        time.sleep(EVENT_DELAY)

        with lock:
            for idx, img in enumerate(reversed(buffer)):
                img_path = os.path.join(dtime_path, f"img_{idx}{IMG_TYPE}")
                if isinstance(img, str):
                    # placeholder values captured when no camera is present
                    with open(img_path + ".txt", "w") as f:
                        f.write(img)
                else:
                    cv2.imwrite(img_path, img)
            buffer.clear()

        self.logger.debug("Wrote %d images to %s", idx + 1, dtime_path)
        self.lockout_until = time.time() + LOCKOUT_DELAY

    def detect_event(self, buffer: Deque[str], lock: threading.Lock) -> None:
        """Trigger an event write if not currently locked out."""
        if time.time() < self.lockout_until:
            return
        self.write_images(buffer, lock)

    def power_off(self) -> None:
        self.cam.power_off()
