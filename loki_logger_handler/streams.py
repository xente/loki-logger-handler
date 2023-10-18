import json


class _LokiRequestEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Streams):
            return {"streams": [stream.__dict__ for stream in obj.streams]}
        return json.JSONEncoder.default(self, obj)


class Streams:
    def __init__(self, streams=None):
        if streams is None:
            streams = []
        self.streams = streams

    def addStream(self, stream):
        self.streams.append(stream)

    def addStreams(self, streams):
        self.streams = streams

    def serialize(self):
        return json.dumps(self, cls=_LokiRequestEncoder)
