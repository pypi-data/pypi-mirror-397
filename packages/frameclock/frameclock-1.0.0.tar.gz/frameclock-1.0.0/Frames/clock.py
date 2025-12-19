if __debug__:
    assert not __name__ == "__main__"
from ._internal.core import Clock

target_fps = Clock.target_fps
get_fps = Clock.get_fps
get_elapsed = Clock.get_elapsed
get_delta_time = Clock.get_delta_time
try_frame = Clock.try_frame
try_assert = Clock.try_assert
wait = Clock.wait
loop = Clock.loop

def get_clock():
    return Clock