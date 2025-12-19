# -*- coding: UTF-8 -*-


import logging
import logging.handlers

from .formatter import LevelColorFormatter


LOG_DEFAULT_LOG_FILENAME = ".log"
LOG_DEFAULT_FILE_FORMATTER = logging.Formatter(fmt="[%(asctime)s][%(levelname)1s][%(module)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
LOG_DEFAULT_STREAM_FORMATTER = LevelColorFormatter(fmt="%(message)s")

LOG_DEFAULT_FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_DEFAULT_LOG_FILENAME, when="midnight")
LOG_DEFAULT_FILE_HANDLER.setLevel(logging.NOTSET)
LOG_DEFAULT_FILE_HANDLER.setFormatter(LOG_DEFAULT_FILE_FORMATTER)

LOG_DEFAULT_STREAM_HANDLER = logging.StreamHandler()
LOG_DEFAULT_STREAM_HANDLER.setLevel(logging.WARNING)
LOG_DEFAULT_STREAM_HANDLER.setFormatter(LOG_DEFAULT_STREAM_FORMATTER)


def use_default_file_handler(filename: str = LOG_DEFAULT_LOG_FILENAME):
    if not LOG_DEFAULT_FILE_HANDLER.baseFilename == filename:
        LOG_DEFAULT_FILE_HANDLER.baseFilename = filename
        LOG_DEFAULT_FILE_HANDLER.doRollover()
    if not LOG_DEFAULT_FILE_HANDLER in LOGGER.handlers:
        LOGGER.addHandler(LOG_DEFAULT_FILE_HANDLER)

def use_default_stream_handler():
    if not LOG_DEFAULT_STREAM_HANDLER in LOGGER.handlers:
        LOGGER.addHandler(LOG_DEFAULT_STREAM_HANDLER)

def unuse_default_file_handler():
    LOGGER.removeHandler(LOG_DEFAULT_FILE_HANDLER)

def unuse_default_stream_handler():
    LOGGER.removeHandler(LOG_DEFAULT_STREAM_HANDLER)


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.NOTSET)

