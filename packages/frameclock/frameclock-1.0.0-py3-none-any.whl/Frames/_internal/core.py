if __debug__:
    assert not __name__ == "__main__"
from typing import Final
from collections import deque
from time import monotonic, sleep

BREAK: Final = object()

class FrameCounter:
    def __init__(self, average: int = 50) -> None:
        self.timestamps = deque(maxlen=average)
    def stamp(self) -> float:
        now = monotonic()
        self.timestamps.append(now)
        length = len(self.timestamps)
        if length > 1:
            return (length - 1) / (now - self.timestamps[0])
        else:
            return 0.0
    def __call__(self) -> float:
        return self.stamp()

class FrameLimit:
    def __init__(self, fps: float) -> None:
        assert fps > 0.0
        if fps <= 0:
            raise ValueError("fps must be positive.")
        self.start = monotonic()
        self.next_tick = self.start + 1.0 / fps
        self.fps = fps
        self._delta_time = 0.0
        self._elapsed = 0.0
    @property
    def delta_time(self) -> float:
        return self._delta_time
    @property
    def elapsed(self) -> float:
        return self._elapsed
    def try_frame(self) -> bool:
        now = monotonic()
        if now >= self.next_tick:
            elapsed = now - self.start
            self.next_tick += 1.0 / self.fps
            self._delta_time = elapsed - self._elapsed
            self._elapsed = elapsed
            return True
        return False
    def try_assert(self) -> None:
        assert self.try_frame()
    def wait(self, update: bool = True): # Return value is uncertain
        remaining = self.next_tick - monotonic()
        if remaining > 0:
            sleep(remaining)
        if update:
            return self.try_frame()
    def loop(self, func):
        active = True
        while active:
            if self.try_frame():
                active = not func() == BREAK
    def __call__(self):
        return self.try_frame()

class Clock:
    limiter = None
    counter = FrameCounter()
    @classmethod
    def target_fps(cls, fps: float) -> None:
        if not cls.limiter:
            cls.limiter = FrameLimit(fps)
            return
        assert fps > 0.0
        if fps <= 0:
            raise ValueError("fps must be positive.")
        cls.limiter.fps = fps
    @classmethod
    def get_fps(cls) -> float:
        return cls.counter.stamp()
    @classmethod
    def get_elapsed(cls) -> float:
        return cls.limiter.elapsed
    @classmethod
    def get_delta_time(cls) -> float:
        return cls.limiter.delta_time
    @classmethod
    def try_frame(cls) -> bool:
        return cls.limiter.try_frame()
    @classmethod
    def try_assert(cls) -> None:
        cls.limiter.try_assert()
    @classmethod
    def wait(cls, update: bool = True):
        return cls.limiter.wait(update)
    @classmethod
    def loop(cls, func):
        cls.limiter.loop(func)