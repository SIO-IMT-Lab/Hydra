"""Configuration for the WhiteCapCam module.

Contains
- Camera constants
- Logging constants
"""

########### Camera Constants ###########
# Location of image directory to save images
IMG_DIR = "/media/grant/Extreme Pro/whitecapcam_images"
# Type of image to save to disk
IMG_TYPE = ".png"
# Camera settings
EXPOSURE = 1000
GAIN = 0
BRIGHTNESS = 10
GAMMA = 0.25
FPS = 8
BACKLIGHT = 1
# Camera identifier
CAMERA_ID = "20407408"
# Capture interval in seconds (15 minutes)
CAPTURE_INTERVAL = 15 * 60

########### Logging Constants ###########
# Name of file to log to
LOG_FILE = "wccam"
FILEMODE = "w"
LOGGER_NAME = "WhiteCapCam Logger"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
MESSAGE_FORMAT = "%(asctime)s.%(msecs)03d # %(name)s # %(levelname)s # %(message)s"
