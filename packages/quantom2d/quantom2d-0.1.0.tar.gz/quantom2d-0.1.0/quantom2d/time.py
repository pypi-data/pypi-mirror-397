import time

class Time:
    delta = 0.0
    _last = time.time()

    @staticmethod
    def update():
        now = time.time()
        Time.delta = now - Time._last
        Time._last = now
