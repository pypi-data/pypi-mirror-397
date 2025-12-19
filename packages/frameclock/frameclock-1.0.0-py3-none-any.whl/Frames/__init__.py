"""
Implements frame counter and limiter, `FrameCounter`, `FrameLimit` and `clock`. 
Also implements `BREAK` for custom loops in `FrameLimit`.
"""

# Simple assurance/debug wether the implementation is correct.
if __debug__:
    assert not __name__ == "__main__"
try:
    from ._internal.core import (
        FrameCounter, FrameLimit, BREAK
    )
except Exception as e: # Minimal code necessary
    raise ImportError("Cannot import Frames internals.") from e
try:
    from . import clock
except: # Backup reference will be a object
    from typing import Final
    clock: Final = object()
import sys
if sys.version_info < (3,): # We are unsure it will function at a downgrade like this
    print("Warning: The package 'Frames' is not intended for this version.")

__all__ = (
    "FrameCounter", "FrameLimit",
    "clock", "BREAK"
)