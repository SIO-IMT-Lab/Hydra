from bubblecam import BubbleCam
from state import State
from collections import deque
import threading
import time

if __name__ == "__main__":
    prev_state = State.QUIESCENT
    curr_state = State.STORM

    queue = deque()
    lock = threading.Lock()

    bubblecam = BubbleCam()

    capture_thread = threading.Thread(target=bubblecam.capture_loop, args=(queue, lock))
    write_thread = threading.Thread(target=bubblecam.write_images, args=(queue, lock))

    while True:
        if curr_state == State.STORM and prev_state == State.QUIESCENT:
            capture_thread.start()
            prev_state = State.STORM
        elif curr_state == State.WAVEBREAK:
            write_thread.start()
            write_thread.join()
            curr_state = State.STORM
        time.sleep(0.5)
