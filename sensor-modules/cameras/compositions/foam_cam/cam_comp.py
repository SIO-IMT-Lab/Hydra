import queue
from state import State # Enums: {Quiescent, Storm, Event}

import cv2
from typing import Callable
# import EasyPySpin # PySpin Module
import datetime
from queue import Queue

class Cam():

    def __init__(self, 
                name: str,
                capture_function,
                exposure: int, 
                gain: int, 
                brightness: int, 
                gamma: float, 
                fps: int, 
                backlight: int, 
                event_delay: int,
                image_type: str,
                buffer_size: int):
        """
        Initializes the camera object
        """

        # self.camera = EasyPySpin.VideoCapture(0)
        self.name = name # name of camera (bubble, foam, or whitecap)
        self.capture_function = capture_function
        # self.event_delay = event_delay
        # self.image_type = image_type
        self.buffer_size = buffer_size

        # self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
        # self.camera.set(cv2.CAP_PROP_GAIN, gain)
        # self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        # self.camera.set(cv2.CAP_PROP_GAMMA, gamma)
        # self.camera.set(cv2.CAP_PROP_FPS, fps)
        # self.camera.set(cv2.CAP_PROP_BACKLIGHT, backlight)

    def start_workflow(self, queue):
        self.capture_function(queue)
    
    def capture_image(self):
        """
        Captures an image from the camera and returns it as a numpy array
        """
        success, frame = self.camera.read()
        return success, frame

    def power_off(self):
        """
        Powers off the camera
        """
        self.camera.release()
    
    