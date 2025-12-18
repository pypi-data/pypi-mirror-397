"""
ContextTskTimer to measure time using with statement
"""

from typing import Any

from ..utils.formatting import TskTimerFormat
from .tsktimer import TskTimer


class ContextTskTimer(TskTimer):
    @staticmethod
    def from_tsktimer(tsktimer: TskTimer):
        return ContextTskTimer(tsktimer.unique_id)

    def __enter__(self):
        self.start()
        return self

    def __exit__(
        self, exc_type: Any | None, exc_value: Any | None, traceback: Any | None
    ):
        self.stop()
        assert self.last_result is not None, "Cannot be None"

        print(
            f"Time: {self._result if not self._result else TskTimerFormat.s(self._result)}"
        )
