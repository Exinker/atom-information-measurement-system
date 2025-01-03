
class FakeCallback:

    def __init__(self):
        self._is_called = False

    @property
    def is_called(self) -> bool:
        return self._is_called

    def __call__(self, *args, **kwds):
        self._is_called = True
