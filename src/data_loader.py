"""Readers for the tab-delimited FMG and insole exports."""

from pathlib import Path
import re

import pandas as pd


NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")


def _read_numeric_rows(file_path: str | Path, width: int) -> pd.DataFrame:
    rows: list[list[float]] = []
    with Path(file_path).open("r", errors="ignore") as stream:
        for line in stream:
            values = [float(value) for value in NUMBER.findall(line)]
            if len(values) >= width and len(values) % width == 0:
                rows.extend(values[i : i + width] for i in range(0, len(values), width))
    return pd.DataFrame(rows)


def read_fmg_file(file_path: str | Path) -> pd.DataFrame:
    columns = (["time", "trigger"] + [f"left_ch{i}" for i in range(1, 9)]
               + [f"right_ch{i}" for i in range(1, 9)])
    frame = _read_numeric_rows(file_path, 18)
    frame.columns = columns
    return frame


def read_insole_file(file_path: str | Path) -> pd.DataFrame:
    frame = _read_numeric_rows(file_path, 4)
    frame.columns = ["time", "trigger", "cop", "vgrf"]
    return frame
