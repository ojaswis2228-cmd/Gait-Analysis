"""Reproducible Study 1 segmentation for the complete FMG dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd

from .data_loader import read_fmg_file, read_insole_file


@dataclass(frozen=True)
class Recording:
    subject: str
    population: str
    block: int
    fmg: Path
    left: Path
    right: Path
    max_trials: int


def discover_recordings(root: Path) -> list[Recording]:
    """Find every complete FMG/left/right triplet in every subject folder."""
    provisional: list[Recording] = []
    for directory in sorted(p for p in root.rglob("*") if p.is_dir()):
        subject_match = re.fullmatch(r"Sub(\d+)_(H|A)", directory.name)
        if subject_match is None:
            continue
        grouped: dict[tuple[str, int], dict[str, Path]] = {}
        for path in (p for p in directory.iterdir() if p.is_file()):
            match = re.fullmatch(r"(.+?)_(\d+)(?:_?([LR]))?(?:\.txt)?", path.name, re.I)
            if match:
                key = (match.group(1).lower(), int(match.group(2)))
                grouped.setdefault(key, {})[(match.group(3) or "fmg").lower()] = path
        complete = sorted((block, files) for (_, block), files in grouped.items()
                          if {"fmg", "l", "r"} <= files.keys())
        for index, (block, files) in enumerate(complete):
            next_block = complete[index + 1][0] if index + 1 < len(complete) else 41
            provisional.append(Recording(
                subject=directory.name,
                population="healthy" if subject_match.group(2) == "H" else "amputee",
                block=block, fmg=files["fmg"], left=files["l"], right=files["r"],
                max_trials=max(1, min(40, next_block) - block),
            ))
    return provisional


def trigger_regions(trigger: pd.Series) -> list[tuple[int, int]]:
    active = np.asarray(trigger, dtype=float) >= 0.5
    changes = np.diff(np.r_[False, active, False].astype(np.int8))
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1) - 1
    return list(zip(starts.tolist(), ends.tolist()))


def trial_ranges(frame: pd.DataFrame) -> list[tuple[int, int]]:
    """A trial runs from the leading edge of one marker to the next marker."""
    regions = trigger_regions(frame["trigger"])
    if len(regions) < 2:
        # Several individually exported trials have no marker or only one
        # marker because the file was cropped after acquisition.
        return [(0, len(frame))] if len(frame) else []
    return [(regions[i][0], regions[i + 1][0]) for i in range(0, len(regions) - 1, 2)]


def sample_rate(time: pd.Series) -> float:
    delta = np.diff(np.asarray(time, dtype=float))
    delta = delta[np.isfinite(delta) & (delta > 0)]
    return float(1 / np.median(delta)) if len(delta) else float("nan")


def detect_contacts(vgrf: pd.Series, time: pd.Series) -> tuple[np.ndarray, float, list[int]]:
    signal = np.asarray(vgrf, dtype=float)
    hz = sample_rate(time)
    if not np.isfinite(hz):
        hz = 100.0
    window = max(3, int(round(0.07 * hz)))
    if window % 2 == 0:
        window += 1
    min_gap = max(1, int(round(0.40 * hz)))
    max_stance = max(min_gap + 1, int(round(2.0 * hz)))
    raw_smooth = pd.Series(signal).rolling(window, center=True, min_periods=1).median().to_numpy()

    def crossings(candidate: np.ndarray) -> tuple[float, list[int]]:
        low, high = np.nanpercentile(candidate, [10, 90])
        span = high - low
        if not np.isfinite(span) or span <= 0:
            return float("nan"), []
        off_threshold = low + 0.20 * span
        on_threshold = low + 0.45 * span
        result: list[int] = []
        armed = bool(candidate[0] <= off_threshold)
        for index in range(1, len(candidate)):
            if candidate[index] <= off_threshold:
                armed = True
            if armed and candidate[index - 1] < on_threshold <= candidate[index]:
                if not result or index - result[-1] >= min_gap:
                    future = candidate[index : min(len(candidate), index + max_stance)]
                    if np.any(future <= off_threshold):
                        result.append(index)
                        armed = False
        return float(on_threshold), result

    normal = crossings(raw_smooth)
    inverted = crossings(-raw_smooth)
    # Expected trials contain about ten cycles. Choose the polarity whose count
    # is plausible and closest to eleven contacts.
    threshold, contacts = min((normal, inverted), key=lambda item: abs(len(item[1]) - 11))
    return raw_smooth, threshold, contacts


def map_by_time(indices: list[int], source: pd.DataFrame, target: pd.DataFrame) -> list[int]:
    if not indices or target.empty:
        return []
    source_time = np.asarray(source["time"], dtype=float)
    target_time = np.asarray(target["time"], dtype=float)
    elapsed = source_time[indices] - source_time[0]
    target_elapsed = target_time - target_time[0]
    return np.searchsorted(target_elapsed, elapsed, side="left").clip(0, len(target) - 1).tolist()


def normalize_cycle(values: np.ndarray, points: int = 101) -> np.ndarray:
    old_x = np.linspace(0, 100, len(values))
    new_x = np.linspace(0, 100, points)
    return np.column_stack([np.interp(new_x, old_x, values[:, col]) for col in range(values.shape[1])])


def cycle_label(index: int, count: int) -> str:
    if index == 0:
        return "gait_initiation"
    if index == count - 1:
        return "gait_termination"
    return "unassigned_steady_or_transition"


def process_recording(recording: Recording) -> tuple[list[dict], list[dict], list[dict]]:
    fmg = read_fmg_file(recording.fmg)
    left = read_insole_file(recording.left)
    right = read_insole_file(recording.right)
    ranges = {"fmg": trial_ranges(fmg), "left": trial_ranges(left), "right": trial_ranges(right)}
    # A damaged trigger channel can oscillate with the gait signal (notably the
    # Sub04 left insole). Reconstruct its trial bounds from the clean FMG marker
    # positions rather than pairing hundreds of false trigger regions.
    fmg_count = len(ranges["fmg"])
    for side, frame in (("left", left), ("right", right)):
        if fmg_count and (len(ranges[side]) > 1.5 * fmg_count or len(ranges[side]) < 0.5 * fmg_count):
            scale = len(frame) / len(fmg)
            ranges[side] = [(round(a * scale), min(len(frame), round(b * scale)))
                            for a, b in ranges["fmg"]]
    trial_count = min(*map(len, ranges.values()), recording.max_trials)
    trial_rows: list[dict] = []
    metadata_rows: list[dict] = []
    normalized_rows: list[dict] = []

    for offset in range(trial_count):
        f0, f1 = ranges["fmg"][offset]
        trial_fmg = fmg.iloc[f0:f1].reset_index(drop=True)
        trial_id = recording.block + offset
        side_results: dict[str, tuple[int, int]] = {}
        for side, insole, columns in (
            ("left", left, [f"left_ch{i}" for i in range(1, 9)]),
            ("right", right, [f"right_ch{i}" for i in range(1, 9)]),
        ):
            s0, s1 = ranges[side][offset]
            trial_insole = insole.iloc[s0:s1].reset_index(drop=True)
            _, threshold, contacts = detect_contacts(trial_insole["vgrf"], trial_insole["time"])
            mapped = map_by_time(contacts, trial_insole, trial_fmg)
            valid_pairs = []
            for source_a, source_b, a, b in zip(contacts[:-1], contacts[1:], mapped[:-1], mapped[1:]):
                if b - a < 3 or source_b - source_a < 3:
                    continue
                duration = float(trial_fmg.iloc[b - 1]["time"] - trial_fmg.iloc[a]["time"])
                if 0.4 <= duration <= 2.5:
                    valid_pairs.append((source_a, source_b, a, b))
            side_results[side] = (len(contacts), len(valid_pairs))
            for cycle_index, (source_begin, source_end, begin, end) in enumerate(valid_pairs):
                values = trial_fmg.loc[begin:end - 1, columns].to_numpy(float)
                normalized = normalize_cycle(values)
                insole_values = trial_insole.loc[source_begin:source_end - 1, ["cop", "vgrf"]].to_numpy(float)
                normalized_insole = normalize_cycle(insole_values)
                cycle_id = f"{recording.subject}_T{trial_id:02d}_{side[0].upper()}_C{cycle_index + 1:02d}"
                label = cycle_label(cycle_index, len(valid_pairs))
                metadata_rows.append({
                    "cycle_id": cycle_id, "subject": recording.subject,
                    "population": recording.population, "block": recording.block,
                    "trial": trial_id, "side": side, "cycle_in_trial": cycle_index + 1,
                    "class_label": label, "fmg_start_sample": f0 + begin,
                    "fmg_end_sample_exclusive": f0 + end, "raw_samples": end - begin,
                    "duration_s": float(trial_fmg.iloc[end - 1]["time"] - trial_fmg.iloc[begin]["time"]),
                    "contact_threshold": threshold,
                })
                for point, row in enumerate(normalized):
                    normalized_rows.append({"cycle_id": cycle_id, "gait_cycle_percent": point,
                                            **{f"ch{i+1}": row[i] for i in range(8)},
                                            "cop": normalized_insole[point, 0],
                                            "vgrf": normalized_insole[point, 1]})
        status = "OK" if all(6 <= cycles <= 16 for _, cycles in side_results.values()) else "CHECK"
        trial_rows.append({
            "subject": recording.subject, "population": recording.population,
            "block": recording.block, "trial": trial_id, "status": status,
            "fmg_samples": len(trial_fmg),
            "left_contacts": side_results["left"][0], "left_cycles": side_results["left"][1],
            "right_contacts": side_results["right"][0], "right_cycles": side_results["right"][1],
        })
    return trial_rows, metadata_rows, normalized_rows
