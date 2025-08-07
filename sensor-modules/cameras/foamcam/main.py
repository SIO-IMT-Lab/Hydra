from collections import deque
import threading
import time
import zmq
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
COMMON_DIR = CURRENT_DIR.parent / "common"
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(COMMON_DIR))

from foamcam import FoamCam
from state import State
import config


if __name__ == "__main__":
    prev_state = State.QUIESCENT
    curr_state = State.STORM

    queue = deque()
    lock = threading.Lock()

    foamcam = FoamCam()

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{config.SERVER_IP}:{config.SERVER_PORT}")
    socket.setsockopt(zmq.SUBSCRIBE, b"trigger")

    capture_thread = threading.Thread(target=foamcam.capture_loop, args=(queue, lock))
    capture_started = False

    while True:
        if capture_started and not capture_thread.is_alive():
            foamcam.cam.reset()
            capture_thread = threading.Thread(target=foamcam.capture_loop, args=(queue, lock))
            capture_thread.start()

        try:
            msg = socket.recv_string(flags=zmq.NOBLOCK)
            if msg.startswith("trigger"):
                curr_state = State.WAVEBREAK
        except zmq.Again:
            pass

        if curr_state == State.STORM and prev_state == State.QUIESCENT:
            if not capture_started:
                capture_thread.start()
                capture_started = True
            prev_state = State.STORM
        elif curr_state == State.WAVEBREAK:
            write_thread = threading.Thread(target=foamcam.write_images, args=(queue, lock))
            write_thread.start()
            write_thread.join()
            curr_state = State.STORM
        time.sleep(0.5)

