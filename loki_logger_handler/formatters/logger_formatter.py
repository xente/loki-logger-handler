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

    def __init__(self):
        pass

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
        record_keys = set(record.__dict__.keys())
        custom_fields = record_keys - self.LOG_RECORD_FIELDS

        for key in custom_fields:
            formatted[key] = getattr(record, key)

        # Check if the log level indicates an error (case-insensitive and can be partial)
        if record.levelname.upper().startswith("ER"):
            formatted["file"] = record.filename
            formatted["path"] = record.pathname
            formatted["line"] = record.lineno
            formatted["stacktrace"] = traceback.format_exc()

        return formatted
