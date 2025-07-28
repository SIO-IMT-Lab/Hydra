import logging
import datetime

from .bubblecam_config import LOG_FILE, FILEMODE, MESSAGE_FORMAT, DATE_FORMAT


class Logger:
    """Simple wrapper around :mod:`logging` used by camera modules."""

    def __init__(self, is_cam: bool) -> None:
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        log_filename = f"./logs/{curr_date}_{LOG_FILE}.log"
        open(log_filename, "w").close()
        logging.basicConfig(
            filename=log_filename,
            filemode=FILEMODE,
            format=MESSAGE_FORMAT,
            datefmt=DATE_FORMAT,
            level=logging.DEBUG,
        )
        self.logger = logging.getLogger(__name__)
