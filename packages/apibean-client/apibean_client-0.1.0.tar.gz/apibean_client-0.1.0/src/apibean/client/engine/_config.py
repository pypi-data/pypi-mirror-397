
class Config:
    def __init__(self):
        self._default = dict()
        self._current = dict()

    def default(self, **kwargs):
        self._default.update(**kwargs)

    def update(self, *args, **kwargs):
        self._current.update(*args, **kwargs)

    def __contains__(self, item):
        return item in self._current

    def __getitem__(self, key):
        return self._current.get(key, self._default.get(key, None))

    def __setitem__(self, key, value):
        self._current[key] = value

    def __delitem__(self, key):
        del self._current[key]
