# -*- coding: UTF-8 -*-


import logging


class LevelColorFormatter(logging.Formatter):

    COLOR_RESET = "\033[0m"
    COLOR_RED = "\033[31m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[33m"
    COLOR_BLUE = "\033[34m"
    COLOR_MAGENTA = "\033[35m"
    COLOR_CYAN = "\033[36m"
    COLOR_WHITE = "\033[37m"
    COLORS = [COLOR_CYAN, COLOR_WHITE, COLOR_YELLOW, COLOR_RED]

    def level_color(self, levelno: int) -> str:
        return self.COLORS[min(levelno // 10 - 1, len(self.COLORS) - 1)]

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.level_color(record.levelno)
        formatted_message = f"{level_color}{record.getMessage()}{self.COLOR_RESET}"
        return formatted_message

