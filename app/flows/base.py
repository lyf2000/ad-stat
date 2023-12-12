from typing import Any

from common.mixins import ContextMixin


class BaseBusinessFlow(ContextMixin):
    """
    Базовый класс флоу бизнес логики.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Исполнить логику.
        """
        self._pre_exec(*args, **kwargs)
        result = self._exec(*args, **kwargs)
        self._post_exec(*args, **kwargs)
        return result

    def _exec(self, *args, **kwargs):
        """
        Исполнение логики.
        """

    def _pre_exec(self, *args, **kwargs):
        """
        Преподготовка до самого исполнения.
        """

    def _post_exec(self, *args, **kwargs) -> Any:
        """
        Доплогика после исполнения основной.
        """
