"""
Decorator functions of tsktimer package
"""

from typing import Callable

from ..core.tsktimer import TskTimer
from ..utils.formatting import TskTimerFormat


def timeit(name: str | None = None):
    """
    Helps to measure run time of the function

    :param name: name of the tsktimer
    :type name: str | None
    :return: results of the function, then returns the time in seconds
    :rtype: Generator[Any, Any, float]
    """

    def outer(func: Callable):
        def inner(*args, **kwargs):
            temp_timer = TskTimer(name)
            temp_timer.start()

            return_ = func(*args, **kwargs)

            print(f"Time: {TskTimerFormat.s(temp_timer.stop())}")

            return return_

        return inner

    return outer


def ntimesit(n_times: int = 1, name: str | None = None):
    """
    Helps you measure the time of a function

    First this wrapper will yield results of your function `n_times`
    Then return the total run time your function * `n_times`

    :param n_times: how many times ot repeat
    :type n_times: int
    :param name: name of the tsktimer
    :type name: str | None
    """
    assert n_times > 1, "Cannot run your function 0 or less times"

    def outer(func: Callable):
        def inner(*args, **kwargs):
            temp_timer = TskTimer(name)
            temp_timer.start()

            for _ in range(n_times):
                func(*args, **kwargs)

            return temp_timer.stop()

        return inner

    return outer
