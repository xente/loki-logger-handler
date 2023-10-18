class RecordValueMock:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class LevelObject:
    def __init__(self, name):
        self.name = name


class TimeObject:
    def __init__(self, timestamp):
        self._timestamp = timestamp

    def timestamp(self):
        return self._timestamp


class FileObject:
    def __init__(self, name, path):
        self.name = name
        self.path = path
