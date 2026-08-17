#!/usr/bin/env python3
"""Run Study 1 segmentation across all canonical subject recordings."""

from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from src.study1_segmentation import discover_recordings, process_recording


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("output/study1"))
    args = parser.parse_args()
    root = args.data_root.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    recordings = discover_recordings(root)
    if not recordings:
        raise SystemExit("No canonical FMG/insole recording triplets were found.")

    inventory, trials, cycles, samples = [], [], [], []
    for number, recording in enumerate(recordings, 1):
        print(f"[{number:02d}/{len(recordings):02d}] {recording.subject}, block {recording.block}")
        trial_rows, cycle_rows, sample_rows = process_recording(recording)
        inventory.append({
            "subject": recording.subject, "population": recording.population,
            "block": recording.block, "fmg_file": str(recording.fmg.relative_to(root)),
            "left_insole_file": str(recording.left.relative_to(root)),
            "right_insole_file": str(recording.right.relative_to(root)),
            "maximum_trials_from_filename": recording.max_trials,
            "trials_segmented": len(trial_rows), "cycles_segmented": len(cycle_rows),
        })
        trials.extend(trial_rows)
        cycles.extend(cycle_rows)
        samples.extend(sample_rows)

    pd.DataFrame(inventory).to_csv(args.output / "dataset_inventory.csv", index=False)
    pd.DataFrame(trials).to_csv(args.output / "trial_summary.csv", index=False)
    pd.DataFrame(cycles).to_csv(args.output / "cycle_metadata.csv", index=False)
    pd.DataFrame(samples).to_csv(args.output / "cycles_normalized_101.csv", index=False)
    print(f"Wrote {len(trials)} trials and {len(cycles)} cycles to {args.output}")


if __name__ == "__main__":
    main()
