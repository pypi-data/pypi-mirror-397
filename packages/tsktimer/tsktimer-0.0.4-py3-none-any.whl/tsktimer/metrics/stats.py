"""
Get stat for specific timer
"""

from tsktimer.utils.formatting import TskTimerFormat

from ..core.tsktimer import TskTimer
from .history import TskTimerHistory


def get_stats(timer: TskTimer | str) -> str:
    return_ = ""

    if isinstance(timer, str):
        task = TskTimer(timer)
    else:
        task = timer

    if task.unique_id not in TskTimerHistory.global_history:
        return (
            f"No record found for {timer}\n(Did you start recording in TskTimerHistory)"
        )

    history = TskTimerHistory.global_history[task.unique_id]

    return_ += f"Stats for {task}:\n"
    for record in history:
        return_ += f"{record}\n"
    return_ += f"\nTotal: {len(history)}\n"

    return_ += f"Min: {TskTimerFormat.s(min(history))}\n"
    return_ += f"Max: {TskTimerFormat.s(max(history))}\n"
    return_ += f"Average: {TskTimerFormat.s(sum(history) / len(history))}\n"

    return return_
