"""
TskTimerHistory class that helps you analyze your programs time
"""

from tsktimer.utils.formatting import TskTimerFormat

from ..core.tsktimer import TskTimer


class TskTimerHistory:
    # History only for seconds
    global_history: dict[str, list[float]] = {}

    @staticmethod
    def __recorded_stop(self: TskTimer) -> float:  # pyright: ignore[reportSelfClsParameterName]
        """Should be saved only in seconds"""
        result = self.native_stop()
        TskTimerHistory.global_history[self.unique_id] = (
            TskTimerHistory.global_history.get(self.unique_id, [])
            + [TskTimerFormat.reverse(result)]
        )

        return result

    @staticmethod
    def start_recoding_tsktimer():
        """
        All new TskTimer objects will be recoded in history
        Recommended to call this method at the begging of the program
        """
        TskTimer.native_stop, TskTimer.stop = (
            TskTimer.stop,
            TskTimerHistory.__recorded_stop,
        )

    @staticmethod
    def stop_recording_tsktimer():
        """
        Stop to record new TskTimer objects
        The previous objects that was created while recording will still be recorded
        """

        TskTimer.stop = TskTimer.native_stop
