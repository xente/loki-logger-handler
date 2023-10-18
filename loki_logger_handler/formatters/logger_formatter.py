import traceback


class LoggerFormatter:
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
        formatted = {
            "message": record.msg % record.args,
            "timestamp": record.created,
            "process": record.process,
            "thread": record.thread,
            "function": record.funcName,
            "module": record.module,
            "name": record.name,
            "level": record.levelname,
        }

        record_keys = set(record.__dict__.keys())
        missing_fields = record_keys - self.LOG_RECORD_FIELDS

        for key in missing_fields:
            formatted[key] = getattr(record, key)

        if record.levelname == "ERROR":
            formatted["file"] = record.filename
            formatted["path"] = record.pathname
            formatted["line"] = record.lineno
            formatted["stacktrace"] = traceback.format_exc()

        return formatted
