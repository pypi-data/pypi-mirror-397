# TskTimer

Simple way to measure the speed of you function/task/app/project.
Allows you to analyze every function or even code blocks on how efficient they are.

## Installation

pip install -U tsktimer

## Quick Start

```python
from tsktimer import timeit
import time

@timeit(name="heavy_task")
def heavy_task():
    time.sleep(2)

heavy_task()
```

```bash
Time: 2.000088691711426s
```

## Architecture

- IN CORE:
  - TskTimer: the main class that actually measures time
  - Context: Using ContextTskTimer you can measure time of the code block by just wrapping it using
    `with ContextTskTimer()`
  - Decorator: helps to measure time for functions:
    - timeit - measures the function once and prints result
    - ntimesit - helps to measure time by running function multiple times
- IN METRICS:
  - History: allows you to record all measured time all over the program.
  - Export: you can export all your records into csv and json
  - Stats: shows stats for one single timer
- IN UTILS:
  - Formatting: using TskTimerFormat you can set output to be in seconds or milliseconds
