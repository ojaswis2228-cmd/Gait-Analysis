import re
import pandas as pd


def read_fmg_file(file_path):

    records = []

    with open(file_path, "r", errors="ignore") as file:

        for line in file:

            # Find all numbers in the line
            values = re.findall(
                r"[-+]?(?:\d*\.\d+|\d+\.?\d*)",
                line
            )

            values = [float(value) for value in values]

            # One FMG sample = 18 values
            sample_size = 18

            # Ignore incomplete/header values
            for i in range(0, len(values), sample_size):

                sample = values[i:i + sample_size]

                if len(sample) == sample_size:
                    records.append(sample)

    columns = (
        ["time", "trigger"]
        + [f"left_ch{i}" for i in range(1, 9)]
        + [f"right_ch{i}" for i in range(1, 9)]
    )

    df = pd.DataFrame(records, columns=columns)

    return df