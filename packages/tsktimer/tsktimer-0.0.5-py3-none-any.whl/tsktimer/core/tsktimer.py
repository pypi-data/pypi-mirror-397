"""
Main class
"""

import time
import uuid

from ..exceptions import TimerAlreadyStarted, TimerNotStarted
from ..utils.formatting import TskTimerFormat


class TskTimer:
    __timers: dict[str, float] = {}

    def __init__(self, unique_id: str | None = None):
        if unique_id is None:
            unique_id = str(uuid.uuid4())

        self.__unique_id = unique_id
        self._result: float | None = None

    def __str__(self) -> str:
        return f"TskTimer({self.__unique_id})"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, TskTimer):
            return self.__unique_id == value.__unique_id
        return False

    def start(self):
        """
        starts the timer
        raise TimerAlreadyStarted: if the timer is already started

        :param self: TskTimer object
        """
        if self.__unique_id in TskTimer.__timers:
            raise TimerAlreadyStarted(f"{self} already started")

        TskTimer.__timers[self.__unique_id] = time.time()

    def stop(self) -> float:
        """
        stops the timer
        raise TimerNotStarted: if the timer was not started

        :param self: TskTimer object
        :return: time in seconds
        :rtype: float
        """
        if self.__unique_id not in TskTimer.__timers:
            raise TimerNotStarted(f"{self} not started")

        start_stamp = TskTimer.__timers.pop(self.__unique_id)
        self._result = time.time() - start_stamp

        return TskTimerFormat.f(self._result)

    @property
    def unique_id(self):
        return self.__unique_id

    @property
    def last_result(self):
        """
        Returns the last measurement result.
        returns None: if was cleared or nothing was measured yet

        :param self: TskTimer object
        :return: time in seconds
        :rtype: float | None
        """
        return self._result if not self._result else TskTimerFormat.f(self._result)

    def clear_last_result(self):
        self._result = None

    def native_stop(self) -> float:
        """
        Reserved for **TskTimerHistory**
        """
        return 0
