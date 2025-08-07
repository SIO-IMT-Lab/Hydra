# Python Standard Library Modules
import argparse
import os
import logging
import datetime
import multiprocessing as mp
import shutil
from time import sleep, time

# Copied from cSBC (Will remove unused modules as necessary)
# Third Party Modules
import cv2
import EasyPySpin  # We might be able to remove this

# Local Modules
from ..config import *
from ...common.cam import Cam
from ...common.state import State  # Glider States

class BubbleCam(Cam):
	"""
    Bubble cam class which inherits from Cam
	
    Attributes
    ----------
    
    camera : EasyPySpin.VideoCapture
    exposure : int
    gain : int
    brightness : int
    gamma : float
    fps : int
    backlight : int
    event_delay : int
    image_type : String
    buffer_size : int
    buffer : Deque
	initial_state: State
	is_locked_out: Multiprocessing.Value

    Methods
    -------
    
    power_on()
        creates a camera reference and stores it in the appropriate member variable
    power_off()
        a call to the camera reference's release() method; see cSBC.py
    write_data(file_handler?)
        write the data in the buffer to file
    collect_data()
        continuously log data in a double-ended queue
    set_state(next_state: Enum {Quiescent, Storm, Event})
        changes the state of the cam to the passed parameter
    detect_event()
        triggers the Bubble Cam event response -> collects data and logs event time
    """

	# Initialize Member Variables
	def __init__(self,  
				exposure: int, 
				gain: int, 
				brightness: int, 
				fps: int, 
				backlight: int, 
				event_delay: int,
				image_type: str,
				buffer_size: int,
				initial_state: State):
		super().__init__(exposure, gain, brightness, fps, backlight, event_delay, 
						image_type, buffer_size, initial_state)

		logger = logging.getLogger()
		logger.debug(f"Logger created for {__file__}.")

		# Another process to run collect_data() in the background 
		self.collect_data_proc = mp.Process(
            target=self.collect_data,
            args=(self.glider_state),
        )
		# For locking out the camera when an event occurs
		self.is_locked_out = mp.Value("i", False)

		
	# Methods inherited from Sensor via Cam
	def power_on(self):
		"""
		Creates a camera reference and stores it in the appropriate member variable
		"""
		super().power_on()

		# set the camera settings
		self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
		self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
		self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
		self.camera.set(cv2.CAP_PROP_GAMMA, self.gain)
		self.camera.set(cv2.CAP_PROP_FPS, self.fps)
		self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)

		# Start capturing images via another process
		# The process will run until the instance of BubbleCam is deleted and p1.join() will automatically run.
		# A potential fix to this would be to check current_state at initialization and during set_state()
		# and only start the process when appropriate (Storm, Event).
		self.collect_data_proc.start()
	
	def write_data(self):
		"""
		Write the data in the buffer to file
		"""

		# Create a new directory for this event
		dtime_str = self.getDateTimeIso()
		test_path= os.path.join('', dtime_str)
		os.mkdir(test_path)

		try:
			num_captured = 0 # number images in order
			start_time = time() # time the write speed

			# reverse rolling buffer to get last image captured first and write to disk
			for img in list(reversed(self.buffer)):
				img_str = f"img_{num_captured}" + IMG_TYPE
				img.tofile(os.path.join(test_path, img_str)) 
				num_captured += 1

			write_speed = time() - start_time
			print(f"Wrote {num_captured} images to disk at {test_path} in {write_speed} seconds.")
			shutil.rmtree(test_path) # we don't need to save these images after the test is over
			return num_captured, write_speed
		except:
			self.logger.error("Exception occurred", exc_info=True)
			return 0, None

	def collect_data(self):
		"""
		Continuously log data in a double-ended queue.
		"""
		try:	
			while True:
				if self.glider_state.value == State.STORM:
					# in Storm state read frame, encode image, append to rolling buffer
					# TODO(pkam): check success & result values since these ops can fail
					success, frame = self.camera.read()
					result, img = cv2.imencode(IMG_TYPE, frame)
					self.buffer.append(img)
				elif self.glider_state.value == State.WAVEBREAK:
					# in Wavebreak Event state, call write_data() to store data on disk
					if len(self.buffer) != 0:
						self.logger.debug(f"Writing images to disk.")
						self.write_data() # pass in some file_handler  
						self.buffer.clear()
						self.logger.debug(f"Clear buffer.")
					else:
						self.logger.debug(f"Buffer empty. Did not write any images to disk.")

					# Lockout camera for 60 seconds, but resume storm state.
					# TODO(pkam): Determine what to do if STORM state is NOT the right state to return to. 
					# (i.e.) Storm -> Wavebreak -> Quiescent
					# It's very unlikely that we go from Wavebreak to Quiescent, but it is something to consider. Do we care about this edge case?
					self.set_state(State.STORM)
					self.set_camera_lockout(True)
		except:
			self.logger.error("Exception occurred", exc_info=True)
		# release the camera and exit
		finally:
			self.power_off()
			self.logger.info("Successfully released camera.")
		
	def detect_event(self):
		"""
		Triggers the Bubble Cam event response -> collects data and logs event time.
		State transition only occurs when camera is not in lockout mode.
		"""
		# Only set the state if it's not lockout mode.
		# If it is in lockout mode, use the time delta to see if 1 minute has passed.
		if (bool(self.is_locked_out.value)):
			if (time() - self.time_locked_out > self.event_delay):
				self.set_camera_lockout(False)
		else:
			# set current_state to event state
			self.set_state(State.WAVEBREAK)
			self.logger.info(f"Event triggered at {self.getDateTimeIso()}")

	def set_camera_lockout(self, is_locked_out: bool):
		# set the lockout variable
		with self.is_locked_out.lock():
			self.is_locked_out.value = is_locked_out
		# if lockout mode entered, save the time at which it started for later use in computing total lockout time
		if (is_locked_out):
			self.time_locked_out = time()

	# Misc Helpers
	def getDateTimeIso():
		return datetime.datetime.now().isoformat()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--roll_buf_size', dest='roll_buf_size', action='store_true', default=150,
                        help='Set size of the rolling buffer of images.')
    parser.add_argument('--img_type', dest='img_type', action='store_true', default='.png',
                        help='Set image format.')
    parser.add_argument('--exposure', dest='exposure', action='store_true', default=100000,
                        help='Set camera exposure value.')
    parser.add_argument('--gain', dest='gain', action='store_true', default=10,
                        help='Set camera gain value.')
    parser.add_argument('--brightness', dest='brigtness', action='store_true', default=10,
                        help='Set camera brightness value.')
    parser.add_argument('--gamma', dest='gamma', action='store_true', default=0.25,
                        help='Set camera gamma value.')
    parser.add_argument('--fps', dest='fps', action='store_true', default=8,
                        help='Set camera fps value.')
    parser.add_argument('--backlight', dest='backlight', action='store_true', default=1,
                        help='Set camera backlight value.')
    parser.add_argument('--event_delay', dest='event_delay', action='store_true', default=60,
                        help='Set delay between subsequent events.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    print(
        '''This test uses a modified version of the BubbleCam class implementation to test the
        system write speed for a full buffer after a single event is received.''')

    # init camera
    cam = BubbleCam(
        args['exposure'], 
        args['gain'], 
        args['brightness'], 
        args['fps'], 
        args['backlight'], 
        State.STORM, 
        args['event_delay'], 
        args['img_type'], 
        args['roll_buf_size'])

    cam.power_on()
    cam.set_state(State.STORM)
    # sleep for time it takes to fill up buffer and then a little bit more
    sleep(args['roll_buf_size'] / args['fps'] + 5)
    cam.detect_event()
    cam.power_off()