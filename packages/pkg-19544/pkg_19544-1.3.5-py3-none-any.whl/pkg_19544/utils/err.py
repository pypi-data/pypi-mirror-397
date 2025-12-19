from functools import wraps
from logging import ERROR, basicConfig, getLogger


basicConfig(level=ERROR, format="%(levelname)s: %(message)s (%(filename)s:%(lineno)s)")
logger = getLogger(__name__)


def raise_on_false(exception_type=ValueError, message='Function returned False'):
    """
    Raise an exception if the decorated function returns False.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is False:
                if kwargs.get('enable_log'):
                    logger.error(f'{message}', stacklevel=2)
                raise exception_type(message)
            return result
        return wrapper
    return decorator
