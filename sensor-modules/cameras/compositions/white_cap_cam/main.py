from asyncore import write
from bubblecam import BubbleCam
from logger import Logger
from state import State
from bubblecam_config import *
from collections import deque
import threading
import time

if __name__ == '__main__':

	prev_state = State.QUIESCENT
	curr_state = State.STORM

	# Create a queue for the shared data
	queue = deque()

	# Create a lock for the queue
	lock = threading.Lock()

	#Event loop 
    # TODO: This turns on Bubblecam in all states (might not want that)
	bubblecam = BubbleCam()

	# Create two logger instances for capturing and writing
	# Launch two threads for the capture and write function
	captureThread = threading.Thread(target=bubblecam.capture_function, args=(queue, lock))
	writeThread = threading.Thread(target=bubblecam.write_images, args=(queue, lock))

	# TODO: Change to pub sub message detection
	while True:
		if curr_state == State.STORM and prev_state == State.QUIESCENT:
			# Start the capture thread
			captureThread.start()
			prev_state = State.STORM
			time.sleep(10)
			writeThread.start()
			writeThread.join()

		# Receive wavebreak signal
		# Test receive for now
		elif curr_state == State.WAVEBREAK:
			writeThread.start()
			writeThread.join()
			curr_state = State.STORM
		else:
			continue





			
