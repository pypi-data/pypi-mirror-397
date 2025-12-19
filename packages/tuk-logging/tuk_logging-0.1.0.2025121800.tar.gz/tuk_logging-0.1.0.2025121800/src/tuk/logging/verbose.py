# -*- coding: UTF-8 -*-


import logging
import logging.handlers

from .formatter import LevelColorFormatter

from .logger import LOGGER
from .logger import LOG_DEFAULT_STREAM_HANDLER


NO_VERBOSE = - (logging.WARNING // 10)


def verbose(msg, err: bool = False):
    level = logging.ERROR if err else logging.INFO
    LOGGER.log(level, msg)
    if LOG_DEFAULT_STREAM_HANDLER.level > level:
        if isinstance(LOG_DEFAULT_STREAM_HANDLER.formatter, LevelColorFormatter):
            msg = f"{LOG_DEFAULT_STREAM_HANDLER.formatter.level_color(level)}{msg}{LOG_DEFAULT_STREAM_HANDLER.formatter.COLOR_RESET}"
        print(msg)

def set_verbose_level(verbose: int):
    level = max(0, - NO_VERBOSE * 10 - (verbose*10))
    LOG_DEFAULT_STREAM_HANDLER.setLevel(level)

