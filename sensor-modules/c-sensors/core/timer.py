class Timer:

    def __init__(self, timer_period: float, timer_callback):
        self._timer_period = timer_period
        self._timer_callback = timer_callback
