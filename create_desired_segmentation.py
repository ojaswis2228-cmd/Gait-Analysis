#!/usr/bin/env python3
"""Infer Study 1 phases and create annotated plots resembling the reference."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT = Path("output/study1")
PLOTS = OUT / "annotated_trials"


def infer_phases(group: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    group = group.sort_values("cycle_in_trial").copy()
    n = len(group)
    group["phase_label"] = "unclassified"
    group["label_source"] = "stride_duration_change_point"
    group["phase_confidence"] = 0.0
    if n:
        group.iloc[0, group.columns.get_loc("phase_label")] = "GI"
    if n > 1:
        group.iloc[-1, group.columns.get_loc("phase_label")] = "GT"
    summary = {"cycles": n, "transition_cycle": np.nan, "direction": "unclassified",
               "duration_change_percent": np.nan, "confidence": 0.0}
    if n < 7:
        return group, summary

    durations = group["duration_s"].to_numpy(float)
    candidates = range(3, n - 3)
    scores = []
    for split in candidates:
        before = durations[1:split]
        after = durations[split + 1:-1]
        score = ((before - np.mean(before)) ** 2).sum() + ((after - np.mean(after)) ** 2).sum()
        scores.append((score, split))
    _, transition = min(scores)
    first_median = float(np.median(durations[1:transition]))
    second_median = float(np.median(durations[transition + 1:-1]))
    change = abs(second_median - first_median) / max(first_median, second_median, 1e-9)
    confidence = float(np.clip(change / 0.20, 0, 1))
    first = "SSSW" if first_median < second_median else "SSLW"
    second = "SSLW" if first == "SSSW" else "SSSW"
    direction = "SLT" if first == "SSSW" else "LST"
    labels = ["GI"] + [first] * (transition - 1) + [direction]
    labels += [second] * (n - transition - 2) + ["GT"]
    group["phase_label"] = labels
    group["phase_confidence"] = confidence
    summary = {"cycles": n, "transition_cycle": transition + 1, "direction": direction,
               "duration_change_percent": 100 * change, "confidence": confidence}
    return group, summary


def robust_scale(values: np.ndarray) -> np.ndarray:
    low, high = np.nanpercentile(values, [5, 95])
    if not np.isfinite(high - low) or high <= low:
        return np.zeros_like(values)
    return np.clip((values - low) / (high - low), 0, 1)


def main() -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(OUT / "cycle_metadata.csv")
    labelled, summaries = [], []
    trial_keys = ["subject", "population", "block", "trial"]
    for trial_key, trial_group in metadata.groupby(trial_keys, sort=True):
        side_results = {}
        for side, group in trial_group.groupby("side"):
            side_results[side] = infer_phases(group)
        classified = [(side, summary) for side, (_, summary) in side_results.items()
                      if summary["direction"] != "unclassified"]
        chosen_direction = max(classified, key=lambda item: item[1]["confidence"])[1]["direction"] if classified else "unclassified"
        for side, (result, summary) in side_results.items():
            if chosen_direction != "unclassified" and summary["direction"] != "unclassified":
                transition = int(summary["transition_cycle"]) - 1
                n = len(result)
                first = "SSSW" if chosen_direction == "SLT" else "SSLW"
                second = "SSLW" if first == "SSSW" else "SSSW"
                result["phase_label"] = (["GI"] + [first] * (transition - 1)
                                         + [chosen_direction]
                                         + [second] * (n - transition - 2) + ["GT"])
                summary["direction"] = chosen_direction
            labelled.append(result)
            summaries.append(dict(zip(trial_keys, trial_key)) | {"side": side} | summary)
    labels = pd.concat(labelled, ignore_index=True)
    labels.to_csv(OUT / "cycle_phase_labels.csv", index=False)
    pd.DataFrame(summaries).to_csv(OUT / "phase_summary.csv", index=False)

    samples = pd.read_csv(OUT / "cycles_normalized_101.csv")
    label_lookup = labels.set_index("cycle_id")["phase_label"]
    meta_lookup = labels.set_index("cycle_id")[["subject", "trial", "side", "cycle_in_trial"]]
    samples = samples.join(meta_lookup, on="cycle_id", validate="many_to_one")
    channels = [f"ch{i}" for i in range(1, 9)] + ["cop", "vgrf"]
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for (subject, trial), trial_data in samples.groupby(["subject", "trial"], sort=True):
        fig, axes = plt.subplots(2, 1, figsize=(16, 8), sharex=True, sharey=True)
        for axis, side in zip(axes, ("left", "right")):
            side_data = trial_data[trial_data["side"] == side].sort_values(
                ["cycle_in_trial", "gait_cycle_percent"])
            if side_data.empty:
                axis.text(.5, .5, "No complete cycles", transform=axis.transAxes, ha="center")
                continue
            ncycles = int(side_data["cycle_in_trial"].max())
            x = (side_data["cycle_in_trial"].to_numpy() - 1) * 101 + side_data["gait_cycle_percent"].to_numpy()
            for color, channel in zip(colors, channels):
                axis.plot(x, robust_scale(side_data[channel].to_numpy(float)),
                          color=color, linewidth=0.8, alpha=0.9, label=channel.upper())
            cycle_ids = side_data.drop_duplicates("cycle_id").sort_values("cycle_in_trial")["cycle_id"]
            phase_runs, last = [], None
            for position, cycle_id in enumerate(cycle_ids):
                phase = label_lookup.loc[cycle_id]
                if phase != last:
                    phase_runs.append((position, phase))
                    last = phase
            phase_runs.append((len(cycle_ids), "END"))
            for (start, phase), (end, _) in zip(phase_runs[:-1], phase_runs[1:]):
                x0, x1 = start * 101, end * 101
                axis.axvline(x0, color="black", linestyle="--", linewidth=1)
                axis.text((x0 + x1) / 2, 1.035, phase, ha="center", va="bottom", fontweight="bold")
            axis.axvline(ncycles * 101, color="black", linestyle="--", linewidth=1)
            axis.set_title(f"{subject} trial {trial:02d} - {side} side")
            axis.set_ylabel("Normalized amplitude")
            axis.set_ylim(-0.05, 1.15)
            axis.grid(alpha=0.15)
        axes[0].legend(ncol=5, fontsize=8, loc="lower center")
        axes[-1].set_xlabel("Concatenated normalized gait cycles (101 points each)")
        fig.suptitle("Study 1 inferred segmentation (direction inferred from stride duration)", fontsize=13)
        fig.tight_layout()
        fig.savefig(PLOTS / f"{subject}_trial_{int(trial):02d}_annotated.png", dpi=130)
        plt.close(fig)
    print(f"Wrote {len(labels)} labelled cycles and {len(list(PLOTS.glob('*.png')))} annotated plots")


if __name__ == "__main__":
    main()
