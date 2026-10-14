import threading

_streams = set()
_lock = threading.Lock()


def register(stream):
    with _lock:
        _streams.add(stream)


def unregister(stream):
    with _lock:
        _streams.discard(stream)


def stop_all():
    with _lock:
        streams = list(_streams)
    for s in streams:
        try:
            s.abort()
        except Exception:
            pass