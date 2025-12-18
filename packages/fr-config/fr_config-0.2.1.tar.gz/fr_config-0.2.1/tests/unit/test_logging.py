import sys
from fr_config._internal.utils import logging


def test_get_logger():
    LOGGER = logging.get_logger("fr_config.test")
    # Test the formatter is added to the parent only
    assert not LOGGER.handlers
    assert LOGGER.parent.handlers
    assert LOGGER.parent.handlers[0].formatter == logging.FORMATTER


def test_get_log_file():
    log_file = logging.get_logfile("fr_config.test")
    assert not log_file.exists()
    assert log_file.parent == logging.LOG_DIR


def test_std_logger():
    logger = logging.get_logger("fr_config.test.file", log_to_file=True)
    log_file = logging.get_logfile("fr_config.test.file")
    assert log_file.exists()
    logging.StdLogger.initialize(logger)
    assert isinstance(sys.stdout, logging.StdLogger)
    assert isinstance(sys.stderr, logging.StdLogger)
    assert sys.stdout._logger == logger
    print("TEST")
    logging.StdLogger.pop()
    assert not isinstance(sys.stdout, logging.StdLogger)
    assert not isinstance(sys.stderr, logging.StdLogger)

    with log_file.open("r", encoding="UTF-8") as f:
        assert "TEST" in f.read()
