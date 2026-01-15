import logging
from abc import ABC, abstractmethod


class LogFormatter(ABC):
    @abstractmethod
    def format(self, record):
        # type: (logging.LogRecord) ->  dict | dict
        """
        Format a log record into a structured dictionary.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            (tuple): A tuple of dictionary representation of the log record and the extracted loki metadata
        """
        raise NotImplementedError
