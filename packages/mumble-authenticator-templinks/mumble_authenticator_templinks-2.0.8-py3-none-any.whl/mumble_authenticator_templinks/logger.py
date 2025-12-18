from logging import getLogger

from Ice import Logger


class AppLogger(Logger):
    """
    Logger implementation to pipe Ice log messages into
    our own log
    """

    def __init__(self):
        super().__init__()
        self._log = getLogger(__name__)

    def _print(self, message):
        self._log.info(message)

    def trace(self, category, message):
        self._log.debug("Trace %s: %s", category, message)

    def warning(self, message):
        self._log.warning(message)

    def error(self, message):
        self._log.error(message)
