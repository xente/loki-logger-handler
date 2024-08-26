class RecordValueMock(object):  # Explicitly inherit from object for Python 2.7 compatibility
    def __init__(self, id, name):
        self.id = id
        self.name = name


class LevelObject(object):  # Explicitly inherit from object for Python 2.7 compatibility
    def __init__(self, name):
        self.name = name


class TimeObject(object):  # Explicitly inherit from object for Python 2.7 compatibility
    def __init__(self, timestamp):
        self._timestamp = timestamp

    def timestamp(self):
        return self._timestamp


class FileObject(object):  # Explicitly inherit from object for Python 2.7 compatibility
    def __init__(self, name, path):
        self.name = name
        self.path = path
