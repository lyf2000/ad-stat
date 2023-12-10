import logging
from typing import Any, Callable


# TODO: fix with childs overriding
class MethodCallLogger:
    def __init__(self, template: str, f: Callable) -> None:
        self._logger = logging.getLogger(__name__)
        self._template = template
        self._f = f

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._logger.info(self._template.format(*args, **kwargs))
        return self._f(*args, **kwargs)
