from typing import Callable, Type, TypeVar

Error = TypeVar("Error", bound=Exception)


class BaseAPIError(Exception):
    msg: str = ""
    except_: tuple[Type[Error]] = tuple()

    @classmethod
    def handle(cls, *args, exc: Exception, func_: Callable, raise_=True, logger=None, **kwargs):
        cls.handle_(*args, exc=exc, func_=func_, raise_=raise_, **kwargs)

    @classmethod
    def handle_(cls, *args, exc: Exception, func_: Callable, raise_=True, logger=None, **kwargs):
        msg = f"{'-'*10}\n\n{cls.msg}\n\n{exc}\n\n{func_}\n{args}\n{kwargs}\n\n{'-'*10}\n\n"
        if not raise_:
            if logger:
                logger.warn(msg)
                return
        raise cls()


class UnexpectedAPIError(BaseAPIError):
    msg = "Unhandled error!"
