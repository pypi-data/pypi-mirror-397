from collections.abc import Callable
from functools import wraps
from threading import Lock, Semaphore


def limit_concurrency(concurrency_limit: int):
    semaphore = Semaphore(concurrency_limit)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with semaphore:
                return fn(**kwargs)

        return wrapper

    return decorator
