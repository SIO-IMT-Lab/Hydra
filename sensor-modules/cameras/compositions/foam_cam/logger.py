import logging
from bubblecam_config import * # Cam config constants
import time
import os
import datetime
from queue import Queue
import threading
lock = threading.Lock()

class Logger():

    def __init__(self, isCam: bool):
        currDate = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        LOG_FILENAME = f'./logs/{currDate}_{LOG_FILE}.log'
        open(LOG_FILENAME, 'w')

        # Create logger
        logging.basicConfig(
                        filename=LOG_FILENAME,
                        filemode=FILEMODE,
                        format=MESSAGE_FORMAT,
                        datefmt=DATE_FORMAT,
                        level=logging.DEBUG,
        )

        self.logger = logging.getLogger()
        self.logger.debug(f"Logger created by {__file__}")