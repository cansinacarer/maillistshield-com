"""Custom decorators for the Mail List Shield application.

This module provides utility decorators used throughout the application.
"""

from threading import Thread


def asyncr(f):
    """Decorator to run a function asynchronously in a separate thread.

    This decorator is primarily used for sending emails without blocking
    the main request thread.

    Args:
        f: The function to be decorated.

    Returns:
        function: A wrapper function that runs the original function in a separate thread.
    """

    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
