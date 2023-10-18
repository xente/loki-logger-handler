import json


class _StreamtEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Stream):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class Stream(object):
    def __init__(self, labels=None):
        if labels is None:
            labels = {}
        self.stream = labels
        self.values = []

    def addLabel(self, key, value):
        self.stream[key] = value

    def appendValue(self, value):
        self.values.append(
            [
                str(int(value.get("timestamp") * 1e9)),
                json.dumps(value, ensure_ascii=False),
            ]
        )

    def serialize(self):
        return json.dumps(self, cls=_StreamtEncoder)
