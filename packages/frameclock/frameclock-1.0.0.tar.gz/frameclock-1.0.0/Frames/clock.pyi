"""You must set a target fps before you can start dissecting frames. 
Since clock is effectively a singleton internally, it becomes impossible 
to thread. Instead, for threading, you should revert back to 
`FrameCounter` and `FrameLimit`. This should introduce maximal performance 
on just python, and should be better typed than the clock, which was 
made for smaller projects. Suchlike those you make in school ;)."""
from typing import Optional, Type, Callable, NoReturn, Any
from ._internal.core import Clock

def target_fps(fps: float) -> None:
    """Set a target fps."""
def get_fps() -> float:
    """Fetch the current fps."""
def get_elapsed() -> float:
    """Fetch the elapsed time since you set target fps."""
def get_delta_time() -> float:
    """Fetch the delta time (time since last frame in seconds)."""
def try_frame() -> bool:
    """Returns True if the frame should be executed."""
def try_assert() -> None:
    """Asserts `try_frame`."""
def wait(update: bool = True) -> Optional[bool]:
    """Wait for the next frame. If `update` is provisioned as True, it will 
    automatically adjust the limiter for the next frame."""
def loop(func: Callable[[], Any]) -> Optional[NoReturn]:
    """Iterate over the given function until it returns a `BREAK`."""
def get_clock() -> Type[Clock]:
    """Retrieve the clock. Unnecessary at best."""