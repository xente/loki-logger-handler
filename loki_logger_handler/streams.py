import json


class _LokiRequestEncoder(json.JSONEncoder):
    """
    A custom JSON encoder for the Streams class.
    This internal class is used to handle the serialization
    of Streams objects into the JSON format expected by Loki.
    """
    def default(self, obj):
        if isinstance(obj, Streams):
            # Convert the Streams object to a dictionary format suitable for Loki
            return {"streams": [stream.__dict__ for stream in obj.streams]}
        # Use the default serialization method for other objects
        return super(_LokiRequestEncoder, self).default(obj)


class Streams(object):  # Explicitly inherit from object for Python 2 compatibility
    """
    A class representing a collection of Stream objects.
    
    Attributes:
        streams (list): A list of Stream objects.
    """
    def __init__(self, streams=None):
        """
        Initialize a Streams object with an optional list of Stream objects.
        
        Args:
            streams (list, optional): A list of Stream objects. Defaults to an empty list.
        """
        self.streams = streams if streams is not None else []

    def add_stream(self, stream):
        """
        Add a single Stream object to the streams list.
        
        Args:
            stream (Stream): The Stream object to be added.
        """
        self.streams.append(stream)

    def set_streams(self, streams):
        """
        Set the streams list to a new list of Stream objects.
        
        Args:
            streams (list): A list of Stream objects to replace the current streams.
        """
        self.streams = streams

    def serialize(self):
        """
        Serialize the Streams object to a JSON string.
        
        Returns:
            str: The JSON string representation of the Streams object.
        """
        return json.dumps(self, cls=_LokiRequestEncoder)
