# Frames

**Frames** is a lightweight Python frame counter and limiter library.  
It provides:

- Frame rate measurement (`FrameCounter`)
- Frame rate limiting (`FrameLimit`)
- A convenient singleton `Clock` for small projects
- Loop utilities with `BREAK` sentinel

## Installation

```bash
pip install frameclock
```

## Usage

```python
from Frames import FrameCounter, FrameLimit, clock, BREAK

# Frame counter
counter = FrameCounter()
print(counter.stamp())

# Frame limiter
limit = FrameLimit(60)
limit.wait(update=True)

# Clock singleton
clock.target_fps(60)
clock.wait(update=True)
```

## Licence

MIT License