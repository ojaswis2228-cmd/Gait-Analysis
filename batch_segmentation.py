from pathlib import Path

import numpy as np
import pandas as pd

from src.data_loader import read_fmg_file, read_insole_file


# ============================================================
# FILES
# ============================================================

subject = Path("Sub01_H")

fmg_file = subject / "abh_1.txt"
left_file = subject / "abh_1L"
right_file = subject / "abh_1R"


# ============================================================
# LOAD DATA
# ============================================================

fmg_df = read_fmg_file(fmg_file)
left_df = read_insole_file(left_file)
right_df = read_insole_file(right_file)


# ============================================================
# FIND TRIGGER REGIONS
# ============================================================

def find_trigger_regions(df):

    trigger = df["trigger"].values

    regions = []

    in_event = False
    start = None

    for i, value in enumerate(trigger):

        if value == 1 and not in_event:
            start = i
            in_event = True

        elif value == 0 and in_event:
            regions.append((start, i - 1))
            in_event = False

    if in_event:
        regions.append((start, len(trigger) - 1))

    return regions


# ============================================================
# SMOOTH vGRF
# ============================================================

def smooth_signal(signal, window=7):

    signal = pd.Series(
        np.asarray(signal, dtype=float)
    )

    return (
        signal
        .rolling(
            window=window,
            center=True,
            min_periods=1
        )
        .mean()
        .to_numpy()
    )


# ============================================================
# DETECT FOOT CONTACTS
# ============================================================

def detect_foot_contacts(vgrf):

    signal = np.asarray(vgrf, dtype=float)

    smoothed = smooth_signal(signal)

    low_level = np.percentile(smoothed, 10)
    high_level = np.percentile(smoothed, 90)

    force_range = high_level - low_level

    low_threshold = (
        low_level
        + 0.25 * force_range
    )

    high_threshold = (
        low_level
        + 0.50 * force_range
    )

    contacts = []

    armed = False

    min_gap = 50
    max_cycle = 200

    last_contact = -min_gap

    for i in range(1, len(smoothed)):

        if smoothed[i] <= low_threshold:
            armed = True

        if (
            armed
            and smoothed[i - 1] < high_threshold
            and smoothed[i] >= high_threshold
            and i - last_contact >= min_gap
        ):

            search_end = min(
                i + max_cycle,
                len(smoothed)
            )

            future = smoothed[i:search_end]

            returns_low = np.any(
                future <= low_threshold
            )

            if returns_low:

                contacts.append(i)

                last_contact = i

                armed = False

    return contacts


# ============================================================
# MAP INSOLE CONTACT TO FMG
# ============================================================

def map_contacts_to_fmg(
    contacts,
    insole_length,
    fmg_length
):

    mapped = []

    for contact in contacts:

        relative_position = (
            contact /
            (insole_length - 1)
        )

        fmg_index = round(
            relative_position
            * (fmg_length - 1)
        )

        mapped.append(fmg_index)

    return mapped


# ============================================================
# GET TRIGGERS
# ============================================================

fmg_regions = find_trigger_regions(fmg_df)
left_regions = find_trigger_regions(left_df)
right_regions = find_trigger_regions(right_df)


print("FMG triggers:", len(fmg_regions))
print("Left triggers:", len(left_regions))
print("Right triggers:", len(right_regions))


# ============================================================
# SAFETY CHECK
# ============================================================

if not (
    len(fmg_regions)
    == len(left_regions)
    == len(right_regions)
):

    raise ValueError(
        "Trigger counts do not match!"
    )


# ============================================================
# PROCESS ALL TRIALS
# ============================================================

summary = []

number_of_trials = (
    len(fmg_regions) // 2
)

print("\nTrials detected:", number_of_trials)


for trial_number in range(number_of_trials):

    marker_1 = trial_number * 2
    marker_2 = marker_1 + 1


    # --------------------------------------------------------
    # FMG TRIAL
    # --------------------------------------------------------

    fmg_start = fmg_regions[marker_1][0]
    fmg_end = fmg_regions[marker_2][0]

    fmg_trial = (
        fmg_df
        .iloc[fmg_start:fmg_end]
        .copy()
    )


    # --------------------------------------------------------
    # LEFT INSOLE TRIAL
    # --------------------------------------------------------

    left_start = left_regions[marker_1][0]
    left_end = left_regions[marker_2][0]

    left_trial = (
        left_df
        .iloc[left_start:left_end]
        .copy()
    )


    # --------------------------------------------------------
    # RIGHT INSOLE TRIAL
    # --------------------------------------------------------

    right_start = right_regions[marker_1][0]
    right_end = right_regions[marker_2][0]

    right_trial = (
        right_df
        .iloc[right_start:right_end]
        .copy()
    )


    # --------------------------------------------------------
    # CONTACT DETECTION
    # --------------------------------------------------------

    left_contacts = detect_foot_contacts(
        left_trial["vgrf"]
    )

    right_contacts = detect_foot_contacts(
        right_trial["vgrf"]
    )


    # --------------------------------------------------------
    # MAP TO FMG
    # --------------------------------------------------------

    left_fmg_contacts = map_contacts_to_fmg(
        left_contacts,
        len(left_trial),
        len(fmg_trial)
    )

    right_fmg_contacts = map_contacts_to_fmg(
        right_contacts,
        len(right_trial),
        len(fmg_trial)
    )


    # --------------------------------------------------------
    # CYCLE COUNTS
    # --------------------------------------------------------

    left_cycles = max(
        0,
        len(left_contacts) - 1
    )

    right_cycles = max(
        0,
        len(right_contacts) - 1
    )


    # --------------------------------------------------------
    # SIMPLE QA FLAG
    # --------------------------------------------------------

    flag = "OK"

    if (
        left_cycles < 3
        or right_cycles < 3
    ):
        flag = "CHECK"

    if abs(
        left_cycles
        - right_cycles
    ) > 3:
        flag = "CHECK"


    # --------------------------------------------------------
    # STORE SUMMARY
    # --------------------------------------------------------

    summary.append({

        "trial":
            trial_number + 1,

        "fmg_samples":
            len(fmg_trial),

        "left_insole_samples":
            len(left_trial),

        "right_insole_samples":
            len(right_trial),

        "left_contacts":
            len(left_contacts),

        "right_contacts":
            len(right_contacts),

        "left_cycles":
            left_cycles,

        "right_cycles":
            right_cycles,

        "status":
            flag
    })


# ============================================================
# SUMMARY TABLE
# ============================================================

summary_df = pd.DataFrame(summary)

print("\n" + "=" * 70)
print("BATCH SEGMENTATION SUMMARY")
print("=" * 70)

print(
    summary_df.to_string(
        index=False
    )
)


# ============================================================
# TOTALS
# ============================================================

print("\n" + "=" * 70)
print("TOTAL SEGMENTATION RESULT")
print("=" * 70)

print(
    "Total left cycles:",
    summary_df["left_cycles"].sum()
)

print(
    "Total right cycles:",
    summary_df["right_cycles"].sum()
)

print(
    "Trials requiring inspection:",
    (summary_df["status"] == "CHECK").sum()
)


# ============================================================
# SAVE SUMMARY
# ============================================================

output_file = (
    "Sub01_H_abh1_segmentation_summary.csv"
)

summary_df.to_csv(
    output_file,
    index=False
)

print(
    "\nSummary saved to:",
    output_file
)