import logging


class Logger():
    def __init__(self, logger: str | logging.Logger, level: str = "DEBUG"):
        if isinstance(logger, str):
            self._logger = logging.getLogger(logger)
            self._logger.addHandler(logging.NullHandler())
        else:
            self._logger = logger

        self._level = logging._nameToLevel[level]

    def log(self, line: str) -> None:
        self._logger.log(self._level, line)


class StdoutLogger(Logger):
    def __init__(self, logger: str | logging.Logger, level: str = "INFO"):
        super().__init__(logger, level)


class StderrLogger(Logger):
    def __init__(self, logger: str | logging.Logger, level: str = "ERROR"):
        super().__init__(logger, level)
