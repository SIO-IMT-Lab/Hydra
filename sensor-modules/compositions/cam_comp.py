import queue
from ..state import State # Enums: {Quiescent, Storm, Event}

from typing import Callable
import EasyPySpin # PySpin Module
import cv2
import datetime
from queue import Queue

class Cam():

    def __init__(self, 
                name: str,
                capture_function: Callable[...],
                exposure: int, 
                gain: int, 
                brightness: int, 
                fps: int, 
                backlight: int, 
                event_delay: int,
                image_type: str,
                buffer_size: int,
                initial_state: State):
        """
        Initializes the camera object
        """

        self.camera = EasyPySpin.VideoCapture(0)
        self.name = name # name of camera (bubble, foam, or whitecap)
        self.capture_function = capture_function
        self.exposure = exposure
        self.gain = gain
        self.brightness = brightness
        self.fps = fps
        self.backlight = backlight
        self.event_delay = event_delay
        self.image_type = image_type
        self.buffer_size = buffer_size
        # self.buffer = deque([], self.buffer_size)
        # self.glider_state = mp.Value("i", initial_state)

        self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.camera.set(cv2.CAP_PROP_GAMMA, self.gain)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        self.camera.set(cv2.CAP_PROP_BACKLIGHT, self.backlight)

    def start_workflow(self, queue):
        self.capture_function(queue)
    
    def capture_image(self):
        """
        Captures an image from the camera and returns it as a numpy array
        """
        return self.camera.read()

    def power_off(self):
        """
        Powers off the camera
        """
        self.camera.release()
    
    def getDateTimeIso():
        """
        Returns the current date and time in ISO format 
        """
        return datetime.datetime.now().isoformat()