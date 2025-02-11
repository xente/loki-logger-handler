import time
import json

# Compatibility for Python 2 and 3
try:
    from time import time_ns  # Python 3.7+
except ImportError:
    import datetime
    def time_ns():
        return int((time.time() + datetime.datetime.now().microsecond / 1e6) * 1e9)


class _StreamEncoder(json.JSONEncoder):
    """
    A custom JSON encoder for the Stream class.
    This is an internal class used to handle the serialization
    of Stream objects into JSON format.
    """
    def default(self, obj):
        if isinstance(obj, Stream):
            return obj.__dict__
        return super(_StreamEncoder, self).default(obj)


class Stream(object):
    """
    A class representing a data stream with associated labels and values.
    
    Attributes:
        stream (dict): A dictionary containing the labels for the stream.
        values (list): A list of timestamped values associated with the stream.
        message_in_json_format (bool): Whether to format log values as JSON.
    """
    def __init__(self, labels=None, loki_metadata=None, message_in_json_format=True):
        """
        Initialize a Stream object with optional labels and metadata.
        
        Args:
            labels (dict, optional): A dictionary of labels for the stream. Defaults to an empty dictionary.
            loki_metadata (dict, optional): A dictionary of metadata for the stream. Defaults to None.
            message_in_json_format (bool, optional): Whether to format log values as JSON. Defaults to True.
        """
        self.stream = labels or {}
        self.values = []
        self.message_in_json_format = message_in_json_format
        if loki_metadata and not isinstance(loki_metadata, dict):
            raise TypeError("loki_metadata must be a dictionary")
        self.loki_metadata = loki_metadata

    def add_label(self, key, value):
        """
        Add a label to the stream.
        
        Args:
            key (str): The label's key.
            value (str): The label's value.
        """
        self.stream[key] = value

    def append_value(self, value, metadata=None):
        """
        Append a value to the stream with a timestamp.
        
        Args:
            value (dict): A dictionary representing the value to be appended. 
                          It should contain a 'timestamp' key.
        """
        try:
            # Convert the timestamp to nanoseconds and ensure it's a string
            timestamp = str(int(value.get("timestamp") * 1e9))
        except (TypeError, ValueError):
            # Fallback to the current time in nanoseconds if the timestamp is missing or invalid
            timestamp = str(time_ns())
        
        formatted_value = json.dumps(value, ensure_ascii=False) if self.message_in_json_format else value
        if metadata or self.loki_metadata:
            # Ensure both metadata and self.loki_metadata are dictionaries (default to empty dict if None)
            metadata = metadata if metadata is not None else {}
            # Make a copy of self.loki_metadata if it is not None, so that we can safely update it
            log_line_metadata = dict(self.loki_metadata) if self.loki_metadata is not None else {}

            # Merge metadata into global metadata, override global values from log line metadata values
            log_line_metadata.update(metadata)
            
            # Transform all non-string values to strings, Grafana Loki does not accept non str values
            formatted_metadata =  {key: str(value) for key, value in log_line_metadata.items()}

            self.values.append([timestamp, formatted_value, formatted_metadata])
        else:
            self.values.append([timestamp, formatted_value])

    def serialize(self):
        """
        Serialize the Stream object to a JSON string.
        
        Returns:
            str: The JSON string representation of the Stream object.
        """
        return json.dumps(self, cls=_StreamEncoder)
