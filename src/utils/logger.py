import os
import logging.config
from logging.handlers import TimedRotatingFileHandler

LOG_COLORS_CONFIG = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}

DEFAULT_LOGGER_NAME = "bot_louise"

DEFAULT_PRINT_FORMAT = "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t%(message)s"
# DEFAULT_PRINT_FORMAT = "\033[1;33m[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t\033[0m%(message)s"
DEFAULT_FILE_FORMAT = "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t%(message)s"

DEFAULT_FILE_HANDLER = {
    # 要实例化的Handler
    "handler": TimedRotatingFileHandler,
    # 可选 Default to DEFAULT_FILE_FORMAT
    "format": DEFAULT_PRINT_FORMAT,
    # 可选 Default to DEBUG
    "level": logging.DEBUG,
    # 以下是Handler相关参数
    "when": "D",
    "backupCount": 30,
    "encoding": "utf-8",
    # *特殊* 对于filename参数，其中如有 %(name)s 会在实例化阶段填入相应的日志name
    "filename": os.path.join(os.getcwd() + "/logs", "bot_louise.log"),
}