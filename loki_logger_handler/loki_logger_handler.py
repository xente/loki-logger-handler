import queue
import threading
import time
import logging
import atexit
from loki_logger_handler.formatters.logger_formatter import LoggerFormatter
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.streams import Streams
from loki_logger_handler.loki_request import LokiRequest
from loki_logger_handler.stream import Stream


class LokiLoggerHandler(logging.Handler):
    def __init__(
        self,
        url,
        labels,
        labelKeys=None,
        timeout=10,
        compressed=True,
        defaultFormatter=LoggerFormatter(),
        additional_headers=dict()
    ):
        super().__init__()

        if labelKeys is None:
            labelKeys = {}

        self.labels = labels
        self.labelKeys = labelKeys
        self.timeout = timeout
        self.logger_formatter = defaultFormatter
        self.request = LokiRequest(url=url, compressed=compressed, additional_headers=additional_headers)
        self.buffer = queue.Queue()
        self.flush_thread = threading.Thread(target=self._flush, daemon=True)
        self.flush_thread.start()

    def emit(self, record):
        self._put(self.logger_formatter.format(record))

    def _flush(self):
        atexit.register(self._send)

        flushing = False
        while True:
            if not flushing and not self.buffer.empty():
                flushing = True
                self._send()
                flushing = False
            else:
                time.sleep(self.timeout)

    def _send(self):
        temp_streams = {}

        while not self.buffer.empty():
            log = self.buffer.get()
            if log.key not in temp_streams:
                stream = Stream(log.labels)
                temp_streams[log.key] = stream

            temp_streams[log.key].appendValue(log.line)

        if temp_streams:
            streams = Streams(temp_streams.values())
            self.request.send(streams.serialize())

    def write(self, message):
        self.emit(message.record)

    def _put(self, log_record):
        labels = self.labels

        for key in self.labelKeys:
            if key in log_record.keys():
                labels[key] = log_record[key]

        self.buffer.put(LogLine(labels, log_record))


class LogLine:
    def __init__(self, labels, line):
        self.labels = labels
        self.key = self.key_from_lables(labels)
        self.line = line

    def key_from_lables(self, labels):
        key_list = sorted(labels.keys())
        return "_".join(key_list)
