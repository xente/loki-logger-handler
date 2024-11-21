import sys

# Compatibility for Python 2 and 3 queue module
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.7

import threading
import time
import logging
import atexit
from loki_logger_handler.formatters.logger_formatter import LoggerFormatter
from loki_logger_handler.streams import Streams
from loki_logger_handler.loki_request import LokiRequest
from loki_logger_handler.stream import Stream


class LokiLoggerHandler(logging.Handler):
    """
    A custom logging handler that sends logs to a Loki server.

    Attributes:
        labels (dict): Default labels for the logs.
        label_keys (dict): Specific log record keys to extract as labels.
        timeout (int): Timeout interval for flushing logs.
        logger_formatter (logging.Formatter): Formatter for log records.
        request (LokiRequest): Loki request object for sending logs.
        buffer (queue.Queue): Buffer to store log records before sending.
        flush_thread (threading.Thread): Thread for periodically flushing logs.
        message_in_json_format (bool): Whether to format log values as JSON.
    """

    def __init__(
        self,
        url,
        labels,
        label_keys=None,
        additional_headers=None,
        message_in_json_format=True,
        timeout=10,
        compressed=True,
        default_formatter=LoggerFormatter()
    ):
        """
        Initialize the LokiLoggerHandler object.

        Args:
            url (str): The URL of the Loki server.
            labels (dict): Default labels for the logs.
            label_keys (dict, optional): Specific log record keys to extract as labels. Defaults to None.
            additional_headers (dict, optional): Additional headers for the Loki request. Defaults to None.
            message_in_json_format (bool): Whether to format log values as JSON.
            timeout (int, optional): Timeout interval for flushing logs. Defaults to 10 seconds.
            compressed (bool, optional): Whether to compress the logs using gzip. Defaults to True.
            default_formatter (logging.Formatter, optional): Formatter for the log records. If not provided,
                LoggerFormatter or LoguruFormatter will be used.
        """
        super(LokiLoggerHandler, self).__init__()

        self.labels = labels
        self.label_keys = label_keys if label_keys is not None else {}
        self.timeout = timeout
        self.formatter = default_formatter
        self.request = LokiRequest(url=url, compressed=compressed, additional_headers=additional_headers or {})
        self.buffer = queue.Queue()
        self.flush_thread = threading.Thread(target=self._flush)
        
        # Set daemon for Python 2 and 3 compatibility
        self.flush_thread.daemon = True
        self.flush_thread.start()
        
        self.message_in_json_format = message_in_json_format

    def emit(self, record):
        """
        Emit a log record.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        try:
            formatted_record = self.formatter.format(record)
            self._put(formatted_record)
        except Exception:
            pass  # Silently ignore any exceptions

    def _flush(self):
        """
        Flush the buffer by sending the logs to the Loki server.
        This function runs in a separate thread and periodically sends logs.
        """
        atexit.register(self._send)

        while True:
            if not self.buffer.empty():
                try:
                    self._send()
                except Exception:
                    pass  # Silently ignore any exceptions
            else:
                time.sleep(self.timeout)

    def _send(self):
        """
        Send the buffered logs to the Loki server.
        """
        temp_streams = {}

        while not self.buffer.empty():
            log = self.buffer.get()
            if log.key not in temp_streams:
                stream = Stream(log.labels, self.message_in_json_format)
                temp_streams[log.key] = stream

            temp_streams[log.key].append_value(log.line)

        if temp_streams:
            streams = Streams(list(temp_streams.values()))
            self.request.send(streams.serialize())

    def write(self, message):
        """
        Write a message to the log.

        Args:
            message (str): The message to be logged.
        """
        self.emit(message.record)

    def _put(self, log_record):
        """
        Put a log record into the buffer.

        Args:
            log_record (dict): The formatted log record.
        """
        labels = self.labels.copy()

        for key in self.label_keys:
            if key in log_record:
                labels[key] = log_record[key]

        self.buffer.put(LogLine(labels, log_record))


class LogLine:
    """
    Represents a single log line with associated labels.

    Attributes:
        labels (dict): Labels associated with the log line.
        key (str): A unique key generated from the labels.
        line (str): The actual log line content.
    """

    def __init__(self, labels, line):
        """
        Initialize a LogLine object.

        Args:
            labels (dict): Labels associated with the log line.
            line (str): The actual log line content.
        """
        self.labels = labels
        self.key = self._key_from_labels(labels)
        self.line = line

    @staticmethod
    def _key_from_labels(labels):
        """
        Generate a unique key from the labels.

        Args:
            labels (dict): Labels to generate the key from.

        Returns:
            str: A unique key generated from the labels.
        """
        key_list = sorted(labels.keys())
        return "_".join(key_list)
