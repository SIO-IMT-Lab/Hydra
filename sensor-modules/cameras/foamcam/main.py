import os
import sys
from collections import deque
import threading
import time
import zmq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from foamcam import FoamCam
from common.state import State


if __name__ == "__main__":
    prev_state = State.QUIESCENT
    curr_state = State.STORM

    queue = deque()
    lock = threading.Lock()

    foamcam = FoamCam()

    # ZMQ subscriber listens for trigger events from the conductivity UI
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://192.168.100.2:5555")
    socket.setsockopt(zmq.SUBSCRIBE, b"trigger")

    capture_thread = threading.Thread(target=foamcam.capture_loop, args=(queue, lock))
    capture_started = False

    while True:
        if capture_started and not capture_thread.is_alive():
            foamcam.cam.reset()
            capture_thread = threading.Thread(target=foamcam.capture_loop, args=(queue, lock))
            capture_thread.start()

        # non-blocking check for trigger messages
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

