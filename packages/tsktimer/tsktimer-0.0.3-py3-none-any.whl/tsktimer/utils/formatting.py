"""
Formatting the time for tsktimer
"""

from typing import Literal


class TskTimerFormat:
    # !!!DO NOT CHANGE FORMAT WHILE (RECORDING + MEASURING)!!!
    # OR HISTORY WILL BE MESSED UP.
    # STOP ALL MEASURING AND ONLY THEN CHANGE FORMAT
    _current_format: Literal["s", "ms"] = "s"

    @staticmethod
    def current_format():
        return TskTimerFormat._current_format

    @staticmethod
    def s_to_ms(s_time: float):
        return s_time * 1000

    @staticmethod
    def ms_to_s(ms_time: float):
        return ms_time / 1000

    @staticmethod
    def s(s_time: float):
        if TskTimerFormat._current_format == "ms":
            s_time = TskTimerFormat.s_to_ms(s_time)
        return f"{s_time}{TskTimerFormat._current_format}"

    @staticmethod
    def f(s_time: float):
        if TskTimerFormat._current_format == "ms":
            return TskTimerFormat.s_to_ms(s_time)
        return s_time

    @staticmethod
    def reverse(time: float):
        if TskTimerFormat._current_format == "ms":
            return TskTimerFormat.ms_to_s(time)
        return time
