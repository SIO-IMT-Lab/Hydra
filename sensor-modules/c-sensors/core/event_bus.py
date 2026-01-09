from collections import defaultdict
from threading import Lock


class PubSub:
    def __init__(self):
        self._topics = defaultdict(list)
        self._lock = Lock()

    def publish(self, topic: str, msg):
        with self._lock:
            for callback in self._topics[topic]:
                callback(msg)

    def subscribe(self, topic: str, callback):
        with self._lock:
            self._topics[topic].append(callback)
