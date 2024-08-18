from threading import Thread

# Allows you to use @asyncr decorator to have it work on a separate thread
def asyncr(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
