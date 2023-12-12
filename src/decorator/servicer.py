from typing import Any, Callable


class Feature(object):
    def __init__(self, func: Callable) -> None:
        self.func = func
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.func(*args, **kwds)
        pass