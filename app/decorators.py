from threading import Thread


def asyncr(f):
    """Decorator to run a function asynchronously.

    We use this decorator to send emails on a separate thread without blocking the main thread.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: A wrapper function that runs the original function in a separate thread.

    """

    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
