import threading
import time


class TTLCache:
    def __init__(self, loader, ttl=60.0, stale_ttl=300.0):
        self._loader = loader
        self._ttl = ttl
        self._stale_ttl = stale_ttl
        self._data = {}
        self._lock = threading.Lock()
        self._refreshing = set()

    def get(self, key):
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if entry and now - entry[1] < self._ttl:
                return entry[0]
            if entry and now - entry[1] < self._stale_ttl:
                if key not in self._refreshing:
                    self._refreshing.add(key)
                    threading.Thread(target=self._refresh, args=(key,), daemon=True).start()
                return entry[0]
        value = self._loader(key)
        with self._lock:
            self._data[key] = (value, time.monotonic())
        return value

    def _refresh(self, key):
        try:
            value = self._loader(key)
            with self._lock:
                self._data[key] = (value, time.monotonic())
        except Exception:
            pass
        finally:
            with self._lock:
                self._refreshing.discard(key)
