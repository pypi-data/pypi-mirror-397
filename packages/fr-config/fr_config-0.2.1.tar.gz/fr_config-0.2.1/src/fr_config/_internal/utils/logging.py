# Copyright (C) 2024 Floating Rock Studio Ltd
# This file has been copied from fr_common.logging
import sys
import logging
import tempfile
from typing import Union
from pathlib import Path

FORMATTER = logging.Formatter("%(asctime)s:%(levelname)s-8s:%(name)s: %(message)s")
LOG_DIR = Path(tempfile.mkdtemp())  # TODO: Should not get created until used
_LOG_FILES = {}


def get_logger(api: str, level=logging.INFO, log_to_file: Union[bool, str, Path] = False) -> logging.Logger:
    """Get the logger for the given api

    Args:
        api(str) api name

    Returns:
        logging Logger
    """
    logger = logging.getLogger(api)
    logger.setLevel(level)
    # Add stream handler to the base logger only if it is not already added
    base_logger = logging.getLogger(api.rsplit(".")[0]) if "." in api else logger
    if not base_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(FORMATTER)
        base_logger.addHandler(handler)
        # base_logger.propagate = False
    if log_to_file:
        if isinstance(log_to_file, (str, Path, bytes)):
            path = Path(log_to_file)
        else:
            path = get_logfile(logger.name)

        file_handler = logging.FileHandler(str(path))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


def get_logfile(api: str) -> Path:
    """Get te log file for the api

    Args:
        api(str) api name

    Returns:
        Path logfile
    """
    if api in _LOG_FILES:
        return _LOG_FILES[api]
    logfile = LOG_DIR / (api + "_log.txt")
    _LOG_FILES[api] = logfile
    return logfile


class StdLogger:
    """A Simple logger to output stdout or stderr statements to a given logger

    Args:
        logger: Logging object
        level: Logging level
        base: parent logger to call after this one
    """

    @classmethod
    def initialize(cls, logger: logging.Logger):
        """Attaches the stdout/stderr to this logger"""
        sys.stdout = cls(logger, logging.INFO, sys.stdout)
        sys.stderr = cls(logger, logging.ERROR, sys.stderr)

    @classmethod
    def pop(cls, recursive: bool = False):
        """Removes the current logger

        Args:
            recursive(bool): Removes all loggers
        """
        if recursive:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            return
        if isinstance(sys.stdout, cls):
            sys.stdout = sys.stdout._base
        if isinstance(sys.stderr, cls):
            sys.stderr = sys.stderr._base

    def __init__(self, logger: logging.Logger, level=logging.INFO, base=None):
        self._logger = logger
        self._level = level
        self._base = base

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            self._logger.log(self._level, line.rstrip())

        if self._base:
            self._base.write(buffer)

    def flush(self):
        if self._base:
            self._base.flush()
