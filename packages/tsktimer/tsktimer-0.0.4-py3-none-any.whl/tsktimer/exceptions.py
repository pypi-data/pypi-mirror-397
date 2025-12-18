"""
Exception classes for tsktimer
"""


class MainTskTimerException(Exception):
    pass


class TimerAlreadyStarted(MainTskTimerException):
    pass


class TimerNotStarted(MainTskTimerException):
    pass


class IncorrectTskTimeFormat(MainTskTimerException):
    pass
