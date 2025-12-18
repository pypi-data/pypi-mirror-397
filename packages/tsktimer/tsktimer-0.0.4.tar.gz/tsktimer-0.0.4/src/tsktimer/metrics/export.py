"""
Export history of timers
"""

import csv
import json

from tsktimer.metrics.history import TskTimerHistory


def export_history_in_json(file_name: str, *json_dump_args, **json_dump_kwargs):
    """
    All the data that was in `file_name` file will be deleted
    """
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(
            TskTimerHistory.global_history, file, *json_dump_args, **json_dump_kwargs
        )

    print(f"History exported to {file_name} in json")


def export_history_in_csv(file_name: str):
    history = TskTimerHistory.global_history
    headers = list(history.keys())
    max_len = max(len(v) for v in history.values())

    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID"] + headers)

        for i in range(max_len):
            row: list = [i]
            for header in headers:
                if i < len(history[header]):
                    row.append(history[header][i])
                else:
                    row.append("")

            writer.writerow(row)

    print(f"History exported to {file_name} in csv")
