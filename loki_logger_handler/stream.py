import json
import time

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
    def __init__(self, labels=None, message_in_json_format=True):
        """
        Initialize a Stream object with optional labels.
        
        Args:
            labels (dict, optional): A dictionary of labels for the stream. Defaults to an empty dictionary.
        """
        self.stream = labels if labels is not None else {}
        self.values = []
        self.message_in_json_format = message_in_json_format

    def add_label(self, key, value):
        """
        Add a label to the stream.
        
        Args:
            key (str): The label's key.
            value (str): The label's value.
        """
        self.stream[key] = value

    def append_value(self, value):
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
                    
        self.values.append([timestamp, formatted_value])

    def serialize(self):
        """
        Serialize the Stream object to a JSON string.
        
        Returns:
            str: The JSON string representation of the Stream object.
        """
        return json.dumps(self, cls=_StreamEncoder)
