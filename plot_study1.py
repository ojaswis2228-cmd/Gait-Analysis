#!/usr/bin/env python3
"""Create subject-level visual QA plots from generated Study 1 outputs."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT = Path("output/study1")
PLOTS = OUTPUT / "plots"


def main() -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(OUTPUT / "cycle_metadata.csv", usecols=["cycle_id", "subject", "side"])
    lookup = metadata.set_index("cycle_id")[["subject", "side"]]
    subjects = sorted(metadata["subject"].unique())
    stats = {(subject, side): {"sum": np.zeros(101), "sum2": np.zeros(101), "count": np.zeros(101)}
             for subject in subjects for side in ("left", "right")}
    for chunk in pd.read_csv(OUTPUT / "cycles_normalized_101.csv",
                             usecols=["cycle_id", "gait_cycle_percent", "ch1"], chunksize=100_000):
        chunk = chunk.join(lookup, on="cycle_id", validate="many_to_one")
        grouped = chunk.groupby(["subject", "side", "gait_cycle_percent"])["ch1"].agg(["sum", "count"])
        squared = chunk.assign(ch1_squared=chunk["ch1"] ** 2).groupby(
            ["subject", "side", "gait_cycle_percent"])["ch1_squared"].sum()
        for (subject, side, point), row in grouped.iterrows():
            stats[(subject, side)]["sum"][int(point)] += row["sum"]
            stats[(subject, side)]["count"][int(point)] += row["count"]
            stats[(subject, side)]["sum2"][int(point)] += squared.loc[(subject, side, point)]

    for subject in subjects:
        fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, sharey=True)
        for axis, side in zip(axes, ("left", "right")):
            values = stats[(subject, side)]
            x = np.arange(101)
            mean = values["sum"] / values["count"]
            variance = np.maximum(0, values["sum2"] / values["count"] - mean ** 2)
            std = np.sqrt(variance)
            cycle_count = int(values["count"][0])
            axis.fill_between(x, mean - std, mean + std, color="#84a9ff", alpha=0.25,
                              label="mean +/- 1 SD")
            axis.plot(x, mean, color="#d100c9", linewidth=2, label="mean channel 1")
            axis.set_title(f"{subject} - {side} FMG ({cycle_count} segmented cycles)")
            axis.set_ylabel("FMG digital value")
            axis.grid(alpha=0.25)
            axis.legend(loc="best")
        axes[-1].set_xlabel("Gait cycle (%)")
        fig.tight_layout()
        fig.savefig(PLOTS / f"{subject}_normalized_fmg_qa.png", dpi=160)
        plt.close(fig)

    counts = metadata.groupby(["subject", "side"]).size().unstack(fill_value=0)
    axis = counts.plot(kind="bar", figsize=(11, 5), color=["#3569c8", "#e2783c"])
    axis.set_title("Segmented gait cycles by subject and side")
    axis.set_xlabel("Subject")
    axis.set_ylabel("Cycles")
    axis.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(PLOTS / "all_subject_cycle_counts.png", dpi=160)
    plt.close()
    print(f"Wrote {len(counts) + 1} plots to {PLOTS}")


if __name__ == "__main__":
    main()
