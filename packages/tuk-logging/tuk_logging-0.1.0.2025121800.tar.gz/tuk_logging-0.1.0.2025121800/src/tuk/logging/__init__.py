# -*- coding: UTF-8 -*-


__author__ = "Tarcadia"
__url__ = "https://github.com/Tarcadia/tuk-logging"
__copyright__ = "Copyright 2025"
__credits__ = ["Tarcadia"]
__license__ = "MIT"
__version__ = "0.1.0"


import logging
from logging import *

from .formatter import LevelColorFormatter
from .logger import use_default_file_handler
from .logger import use_default_stream_handler
from .logger import unuse_default_file_handler
from .logger import unuse_default_stream_handler
from .verbose import verbose
from .verbose import set_verbose_level
from .traceback import traceback
from .traceback import tracebackonce

from .verbose import NO_VERBOSE
from .logger import LOGGER


__all__ = [
    *logging.__all__,
    "LevelColorFormatter",
    "use_default_file_handler",
    "use_default_stream_handler",
    "unuse_default_file_handler",
    "unuse_default_stream_handler",
    "verbose",
    "set_verbose_level",
    "traceback",
    "tracebackonce",
    "NO_VERBOSE",
    "LOGGER",
]

