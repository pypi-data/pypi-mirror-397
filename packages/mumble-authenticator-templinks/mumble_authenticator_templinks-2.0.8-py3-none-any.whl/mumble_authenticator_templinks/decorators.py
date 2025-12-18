from functools import wraps
from logging import critical
from typing import Any, Callable, Optional, Tuple, Type

import Ice
from eveo7_mumbleserver_ice import InvalidSecretException


def check_secret(secret: Optional[str] = None) -> Callable[[Callable], Callable]:
    """
    Parameterized decorator that checks whether the server transmitted the right secret
    if a secret is supposed to be used.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current = kwargs.get("current", args[-1] if args else None)

            if secret and (not current or current.ctx.get("secret") != secret):
                critical("Server transmitted invalid secret. Possible injection attempt.")
                raise InvalidSecretException()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def fortify_ice(
    retval: Optional[Any] = None, exceptions: Tuple[Type[Exception], ...] = (Ice.Exception,)
) -> Callable[[Callable], Callable]:
    """
    Decorator that catches exceptions, logs them, and returns a safe retval
    value. This helps prevent the authenticator from getting stuck in
    critical code paths. Only exceptions that are instances of classes
    given in the exceptions list are not caught.

    The default is to catch all non-Ice exceptions.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kws: Any) -> Any:
            try:
                return func(*args, **kws)
            except exceptions:
                raise
            except Exception as e:
                critical(f"Unexpected exception in {func.__name__}: {e}")
                return retval

        return wrapper

    return decorator
