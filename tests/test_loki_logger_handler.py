import logging
import unittest
import pytest

try:
    from unittest.mock import patch, Mock, MagicMock, call  # Python 3.x
except ImportError:
    from mock import patch, Mock, MagicMock, call  # Python 2.7

from loki_logger_handler.loki_logger_handler import LogLine, LokiLoggerHandler
from loki_logger_handler.stream import Stream
from loki_logger_handler.formatters.logger_formatter import LoggerFormatter
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter

from tests.helper import LevelObject, RecordValueMock, TimeObject


class CustomFormatter(logging.Formatter):
    def format(self, record):
        return "Custom formatted: {}".format(record.getMessage())


class TestLokiLoggerHandler(unittest.TestCase):
    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch.object(LokiLoggerHandler, "_put")
    @patch("loki_logger_handler.formatters.logger_formatter.LoggerFormatter")
    def test_emit(self, mock_formatter, mock_put, mock_thread):
        # Arrange
        record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
            default_formatter=mock_formatter,
        )
        # Act
        handler.emit(record)

        # Assert
        mock_formatter.format.assert_called_with(record)
        mock_put.assert_called_with(handler.formatter.format.return_value)

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    def test_emit_no_record(self, mock_thread):
        # Arrange
        loki = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
        )

        # Act/Assert
        with pytest.raises(TypeError):
            loki.emit()

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch.object(LokiLoggerHandler, "_put")
    def test_emit_formatter_exception(self, handler, mock_put):
        # Arrange
        handler.logger_formatter.format.side_effect = Exception()

        # Act
        handler.emit(MagicMock())

        # Assert
        mock_put.assert_not_called()

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch.object(LokiLoggerHandler, "_put")
    @patch.object(LokiLoggerHandler, "emit")
    @patch("loki_logger_handler.formatters.loguru_formatter.LoguruFormatter")
    def test_write(self, mock_formatter, mock_emit, mock_put, mock_thread):
        # Arrange
        mock_message = Mock()

        mock_message.record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
            default_formatter=mock_formatter,
        )

        # Act
        handler.write(mock_message)

        # Assert
        mock_emit.assert_called_with(mock_message.record)

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.LogLine")
    def test_put(self, mock_logline, mock_thread):
        # Arrange
        mock_message = Mock()

        mock_message.record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
        )

        mock_queue = Mock()
        handler.buffer = mock_queue
        # Act
        handler._put(mock_message.record)

        expected_labels = {"application": "Test", "environment": "Develop"}
        mock_logline.assert_called_with(expected_labels, mock_message.record)

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.LogLine")
    def test_put_label_key(self, mock_logline, mock_thread):
        # Arrange
        mock_message = Mock()

        mock_message.record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={"function"},
        )

        mock_queue = Mock()
        handler.buffer = mock_queue
        # Act
        handler._put(mock_message.record)

        expected_labels = {
            "application": "Test",
            "environment": "Develop",
            "function": "sample_function",
        }
        mock_logline.assert_called_with(expected_labels, mock_message.record)

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.time")
    def test_flush_happy_path(self, mock_sleep, mock_thread):
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=LoguruFormatter(),
        )
        handler.buffer.put("test_log")  # Add an item to the buffer
        handler._send = Mock()  # Mock the _send method
        handler.timeout = 5

        mock_queue = Mock()
        handler.buffer = mock_queue
        handler.buffer.empty.side_effect = [False, True]

        mock_sleep.sleep.side_effect = Exception("Break the loop")
        try:
            handler._flush()
        except Exception as e:
            self.assertEqual(str(e), "Break the loop")

        mock_sleep.sleep.assert_called_with(handler.timeout)
        handler._send.assert_called_once()

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.Streams")
    @patch("loki_logger_handler.loki_logger_handler.Stream")
    @patch("loki_logger_handler.loki_logger_handler.LokiRequest")
    def test_send_diff_labels(
        self, mock_lokirequest, mock_stream, mock_streams, mock_thread
    ):
        message_in_json_format = True
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=LoguruFormatter(),
            message_in_json_format=message_in_json_format
        )

        record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }

        mock_queue = Mock()
        handler.buffer = mock_queue
        handler.buffer.empty.side_effect = [False, False, True]

        # Arrange
        log1 = LogLine({"label1": "value1"}, record)
        log2 = LogLine({"label2": "value2"}, record)
        handler.buffer.get.side_effect = [log1, log2]

        # Act
        handler._send()

        # Assert

        expected_streams = {
            log1.key: mock_stream.return_value,
            log2.key: mock_stream.return_value,
        }
        expected_streams = list(expected_streams.values())
        actual_streams = list(mock_streams.call_args[0][0])
        self.assertEqual(expected_streams, actual_streams)

        mock_stream.assert_has_calls(
            [
                call(log1.labels, message_in_json_format),
                call().append_value(log1.line),
                call(log2.labels, message_in_json_format),
                call().append_value(log2.line),
            ]
        )

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.Streams")
    @patch("loki_logger_handler.loki_logger_handler.Stream")
    @patch("loki_logger_handler.loki_logger_handler.LokiRequest")
    def test_send_same_labels(
        self, mock_lokirequest, mock_stream, mock_streams, mock_thread
    ):
        message_in_json_format = True
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=LoguruFormatter(),
            message_in_json_format=message_in_json_format
        )

        record = {
            "level": LevelObject(name="INFO"),
            "message": "Sample error message1",
            "time": TimeObject("2023-10-12T10:00:00Z"),
            "process": RecordValueMock(123, "123"),
            "thread": RecordValueMock(456, "456"),
            "function": "sample_function",
            "module": "sample_module",
            "name": "sample_name",
            "extra": {},
        }

        mock_queue = Mock()
        handler.buffer = mock_queue
        handler.buffer.empty.side_effect = [False, False, True]

        log1 = LogLine({"label1": "value1"}, record)
        log2 = LogLine({"label1": "value2"}, record)
        handler.buffer.get.side_effect = [log1, log2]

        handler._send()

        expected_streams = {
            log1.key: mock_stream.return_value,
            log2.key: mock_stream.return_value,
        }
        expected_streams = list(expected_streams.values())
        actual_streams = list(mock_streams.call_args[0][0])
        self.assertEqual(expected_streams, actual_streams)

        mock_stream.assert_has_calls([call(log1.labels, message_in_json_format)])

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch("loki_logger_handler.loki_logger_handler.Streams")
    def test_send_empty_buffer(self, mock_streams, mock_thread):
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=LoguruFormatter(),
        )

        mock_queue = Mock()
        handler.buffer = mock_queue

        handler._send()

        mock_streams.assert_not_called()

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    def test_custom_formatter(self, mock_thread):
        # Arrange
        custom_formatter = CustomFormatter()
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
            default_formatter=custom_formatter,
        )

        record = Mock()
        record.getMessage.return_value = "Test message"

        # Act
        handler.emit(record)

        # Assert
        formatted_message = handler.formatter.format(record)
        self.assertEqual(formatted_message, "Custom formatted: Test message")

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    def test_empty_buffer(self, mock_thread):
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=Mock(),  # Mock the formatter to avoid actual formatting
        )

        handler._send = Mock()  # Mock the _send method
        handler.buffer.empty = Mock(return_value=True)  # Buffer is empty

        # Call _flush directly and then immediately break out of the loop
        with patch("loki_logger_handler.loki_logger_handler.time.sleep", side_effect=Exception("StopIteration")):
            try:
                handler._flush()
            except Exception as e:
                self.assertEqual(str(e), "StopIteration")

        handler._send.assert_not_called()  # _send should not be called

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch.object(LokiLoggerHandler, "_put")
    def test_formatter_exception(self, mock_put, mock_thread):
        handler = LokiLoggerHandler(
            "http://test_url",
            labels={"label1": "value1"},
            default_formatter=LoguruFormatter(),
        )

        record = MagicMock()
        handler.formatter.format = Mock(side_effect=Exception("Formatter Error"))

        handler.emit(record)

        mock_put.assert_not_called()  # The log should not be added to the buffer

    @patch("loki_logger_handler.loki_logger_handler.threading.Thread")
    @patch.object(LokiLoggerHandler, "_put")
    @patch("loki_logger_handler.formatters.logger_formatter.LoggerFormatter")
    def test_emit_with_custom_formatter(self, mock_formatter, mock_put, mock_thread):
        # Arrange
        custom_formatter = CustomFormatter()
        handler = LokiLoggerHandler(
            url="your_url",
            labels={"application": "Test", "environment": "Develop"},
            label_keys={},
            default_formatter=custom_formatter,
        )

        record = Mock()
        record.getMessage.return_value = "Test message"

        # Act
        handler.emit(record)

        # Assert
        mock_put.assert_called_with("Custom formatted: Test message")


if __name__ == "__main__":
    unittest.main()
