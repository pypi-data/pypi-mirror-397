import time

from tsktimer import ntimesit, timeit
from tsktimer.core.context import ContextTskTimer
from tsktimer.metrics.export import export_history_in_csv, export_history_in_json
from tsktimer.metrics.history import TskTimerHistory
from tsktimer.metrics.stats import get_stats
from tsktimer.utils.formatting import TskTimerFormat


@timeit("some_heavy_function")
def some_heavy_function():
    time.sleep(2)


@ntimesit(3, "little_time_function")
def little_time_function():
    time.sleep(1)


if __name__ == "__main__":
    TskTimerHistory.start_recoding_tsktimer()
    TskTimerFormat._current_format = "s"

    some_heavy_function()
    print(f"Small function 3 times. Time {TskTimerFormat.s(little_time_function())}")  # type: ignore
    some_heavy_function()

    TskTimerHistory.stop_recording_tsktimer()

    with ContextTskTimer() as timer:
        print(timer)
        time.sleep(1)

    print(TskTimerHistory.global_history)

    export_history_in_csv("history.csv")
    export_history_in_json("history.json", indent=4)

    print(end="\n\n")
    print(get_stats("some_heavy_function"))
