"""Contains all the necessary configuration aspects for the cSBC module.

Contains
- Camera Constants
- Server Constants
- Logging Constants
- Data Transfer Format
"""

########### Camera constants ###########
# Maximum number of images in rolling buffer at once
ROLL_BUF_SIZE = 10
# Byte threshold for data validation
BYTE_THRESHOLD = 1000
# Location of image directory to save images
IMG_DIR = "bubblecam_images"
# Type of image to save to disk
IMG_TYPE = ".png"
# Amount of time in seconds to wait after event occurs
EVENT_DELAY = 5
# Amount of time in seconds to wait after writing
LOCKOUT_DELAY = 1
# Camera Settings
EXPOSURE = 100000
GAIN = 10
BRIGHTNESS = 10
GAMMA = 0.25
FPS = 8
BACKLIGHT = 1

########### Logging Constants ###########
# Name of file to log to
LOG_FILE = "bcam"
FILEMODE = "w"
LOGGER_NAME = "Bubblecam Logger"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
MESSAGE_FORMAT = "%(asctime)s.%(msecs)03d # %(name)s # %(levelname)s # %(message)s"


