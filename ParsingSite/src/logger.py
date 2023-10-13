"""
Logging module
"""

import logging
import os
import sys


class LogService:
    """
    Logging module configuration
    """
    
    DEFAULT_LOG_LEVEL = logging.DEBUG
    LOG_FILE_NAME = "log.txt"
    DEFAULT_LOG_FORMAT = " %(asctime)s | %(levelname)s | %(filename)-15s:%(lineno)-4d | %(message)s"
    LOG_LEVEL = os.environ.get("LOGLEVEL", DEFAULT_LOG_LEVEL)

    def __init__(self) -> None:
        logging.basicConfig(filename=self.LOG_FILE_NAME,
                            level=self.LOG_LEVEL,
                            filemode='w',
                            format=self.DEFAULT_LOG_FORMAT
                            )

        self.logger = logging.getLogger(__name__)

        logging.getLogger('asyncio').setLevel(logging.WARNING)
        console_handler = logging.StreamHandler(
            sys.stdout)
        console_handler.setLevel(self.LOG_LEVEL)
        console_handler.setFormatter(
            logging.Formatter(self.DEFAULT_LOG_FORMAT))

        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging:
        """
        Creates  logger

        Returns:
            type: logging -> class instance logging            
        """
        return self.logger
