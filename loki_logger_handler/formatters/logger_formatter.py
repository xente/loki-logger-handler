import logging
import traceback

class LoggerFormatter:
    """
    A custom formatter for log records that formats the log record into a structured dictionary.
    """
    LOG_RECORD_FIELDS = {
        "msg",
        "levelname",
        "msecs",
        "name",
        "pathname",
        "filename",
        "module",
        "lineno",
        "funcName",
        "created",
        "thread",
        "threadName",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "args",
        "exc_info",
        "levelno",
        "exc_text",
    }

    def format(self, record):
        """
        Format a log record into a structured dictionary.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            dict: A dictionary representation of the log record.
        """

        formatted = {
            "message": record.getMessage(),
            "timestamp": record.created,
            "process": record.process,
            "thread": record.thread,
            "function": record.funcName,
            "module": record.module,
            "name": record.name,
            "level": record.levelname,
        }

        # Capture any custom fields added to the log record
        loki_metadata = {}
        for key, value in record.__dict__.items():
            if key not in self.LOG_RECORD_FIELDS:
                if key == "loki_metadata" and isinstance(value, dict):
                    loki_metadata = value
                else:
                    formatted[key] = value

        # Check if the log level indicates an error
        if record.levelno >= logging.ERROR:
            formatted["file"] = record.filename
            formatted["path"] = record.pathname
            formatted["line"] = record.lineno
            formatted["stacktrace"] = self._format_stacktrace(record.exc_info)

        return formatted, loki_metadata

    @staticmethod
    def _format_stacktrace(exc_info):
        """
        Format the stacktrace if exc_info is present.

        Args:
            exc_info (tuple or None): Exception info tuple as returned by sys.exc_info().

        Returns:
            str or None: Formatted stacktrace as a string, or None if exc_info is not provided.
        """
        if exc_info:
            return "".join(traceback.format_exception(*exc_info))
        return None
