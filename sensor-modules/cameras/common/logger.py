import datetime
import logging
from pathlib import Path


class Logger:
    """Simple wrapper around :mod:`logging` used by camera modules.

    The behaviour is configured via a ``config`` object which provides the
    logging related attributes (``LOG_FILE``, ``FILEMODE`` etc.).  This mirrors
    the previous behaviour of ``bubblecam_config`` but allows other cameras to
    supply their own settings without duplicating the implementation.
    """

    def __init__(self, config, name: str) -> None:
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        log_dir = Path(__file__).resolve().parent.parent / name / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filename = log_dir / f"{curr_date}_{config.LOG_FILE}.log"
        log_filename.touch()
        logging.basicConfig(
            filename=str(log_filename),
            filemode=config.FILEMODE,
            format=config.MESSAGE_FORMAT,
            datefmt=config.DATE_FORMAT,
            level=logging.DEBUG,
        )
        self.logger = logging.getLogger(__name__)
