from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from src.data_loader import read_fmg_file, read_insole_file


# ============================================================
# DATA PATHS
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
            end = i - 1
            regions.append((start, end))
            in_event = False

    if in_event:
        regions.append((start, len(trigger) - 1))

    return regions


fmg_regions = find_trigger_regions(fmg_df)
left_regions = find_trigger_regions(left_df)
right_regions = find_trigger_regions(right_df)


print("FMG trigger regions:", len(fmg_regions))
print("Left trigger regions:", len(left_regions))
print("Right trigger regions:", len(right_regions))


# ============================================================
# TRIAL 1 = TRIGGER 1 TO TRIGGER 2
# ============================================================

fmg_start = fmg_regions[0][0]
fmg_end = fmg_regions[1][0]

left_start = left_regions[0][0]
left_end = left_regions[1][0]

right_start = right_regions[0][0]
right_end = right_regions[1][0]


fmg_trial = fmg_df.iloc[fmg_start:fmg_end].copy()
left_trial = left_df.iloc[left_start:left_end].copy()
right_trial = right_df.iloc[right_start:right_end].copy()


print("\nTrial 1 shapes:")
print("FMG:", fmg_trial.shape)
print("Left insole:", left_trial.shape)
print("Right insole:", right_trial.shape)


# ============================================================
# NORMALIZED TRIAL TIME
# ============================================================

fmg_trial["trial_progress"] = (
    range(len(fmg_trial))
)

left_trial["trial_progress"] = (
    range(len(left_trial))
)

right_trial["trial_progress"] = (
    range(len(right_trial))
)


# ============================================================
# PLOT TRIAL 1
# ============================================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=(16, 10)
)

axes[0].plot(
    fmg_trial["trial_progress"],
    fmg_trial["left_ch1"]
)

axes[0].set_title("Trial 1 - Left FMG Channel 1")
axes[0].set_ylabel("FMG amplitude")
axes[0].grid(True)


axes[1].plot(
    left_trial["trial_progress"],
    left_trial["vgrf"]
)

axes[1].set_title("Trial 1 - Left Insole vGRF")
axes[1].set_ylabel("vGRF")
axes[1].grid(True)


axes[2].plot(
    right_trial["trial_progress"],
    right_trial["vgrf"]
)

axes[2].set_title("Trial 1 - Right Insole vGRF")
axes[2].set_xlabel("Samples within trial")
axes[2].set_ylabel("vGRF")
axes[2].grid(True)


plt.tight_layout()
plt.show()

# ============================================================
# GAIT CYCLE SEGMENTATION USING vGRF
# ============================================================

import numpy as np


def smooth_signal(signal, window=7):
    """
    Smooth vGRF without creating artificial
    edge effects.
    """

    signal = pd.Series(
        np.asarray(signal, dtype=float)
    )

    smoothed = signal.rolling(
        window=window,
        center=True,
        min_periods=1
    ).mean()

    return smoothed.to_numpy()


def detect_foot_contacts(vgrf):

    signal = np.asarray(vgrf, dtype=float)

    smoothed = smooth_signal(signal, window=7)

    # Robust low and high force levels
    low_level = np.percentile(smoothed, 10)
    high_level = np.percentile(smoothed, 90)

    force_range = high_level - low_level

    # Hysteresis thresholds
    low_threshold = low_level + 0.25 * force_range
    high_threshold = low_level + 0.50 * force_range

    contacts = []

    # The detector becomes "armed" only after the foot
    # reaches the low-force region.
    armed = False

    min_gap = 50
    max_cycle = 200

    last_contact = -min_gap

    for i in range(1, len(smoothed)):

        # Foot is unloaded / in low-force region
        if smoothed[i] <= low_threshold:
            armed = True

        # Detect transition from low force to contact
        if (
            armed
            and smoothed[i - 1] < high_threshold
            and smoothed[i] >= high_threshold
            and i - last_contact >= min_gap
        ):

            # ------------------------------------------------
            # Validate that this really behaves like a gait event:
            # after contact, force should return to low region
            # within a reasonable gait-cycle duration.
            # ------------------------------------------------

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

    return smoothed, high_threshold, contacts

# ============================================================
# DETECT CONTACTS - TRIAL 1
# ============================================================

left_smoothed, left_threshold, left_contacts = (
    detect_foot_contacts(left_trial["vgrf"])
)

right_smoothed, right_threshold, right_contacts = (
    detect_foot_contacts(right_trial["vgrf"])
)


print("\n" + "=" * 60)
print("GAIT CONTACT DETECTION - TRIAL 1")
print("=" * 60)

print("Left threshold:", left_threshold)
print("Left contacts:", len(left_contacts))
print("Left contact indices:", left_contacts)

print()

print("Right threshold:", right_threshold)
print("Right contacts:", len(right_contacts))
print("Right contact indices:", right_contacts)

# ============================================================
# VISUALISE DETECTED FOOT CONTACTS
# ============================================================

fig, axes = plt.subplots(
    2,
    1,
    figsize=(16, 9)
)


# ---------------- LEFT FOOT ----------------

axes[0].plot(
    left_smoothed,
    label="Smoothed vGRF"
)

axes[0].axhline(
    left_threshold,
    linestyle="--",
    label="Adaptive threshold"
)

for contact in left_contacts:

    axes[0].axvline(
        contact,
        linestyle="--",
        alpha=0.6
    )


axes[0].set_title(
    "Left Foot - Detected Foot Contacts"
)

axes[0].set_ylabel("vGRF")

axes[0].legend()

axes[0].grid(True)


# ---------------- RIGHT FOOT ----------------

axes[1].plot(
    right_smoothed,
    label="Smoothed vGRF"
)

axes[1].axhline(
    right_threshold,
    linestyle="--",
    label="Adaptive threshold"
)

for contact in right_contacts:

    axes[1].axvline(
        contact,
        linestyle="--",
        alpha=0.6
    )


axes[1].set_title(
    "Right Foot - Detected Foot Contacts"
)

axes[1].set_xlabel(
    "Samples within Trial 1"
)

axes[1].set_ylabel("vGRF")

axes[1].legend()

axes[1].grid(True)


plt.tight_layout()

plt.show()

# ============================================================
# MAP INSOLE CONTACTS TO FMG
# ============================================================

def map_contacts_to_fmg(
    contacts,
    insole_length,
    fmg_length
):
    """
    Map contact indices from insole trial to corresponding
    FMG trial using relative position within the same
    trigger-defined trial.
    """

    mapped_contacts = []

    for contact in contacts:

        relative_position = (
            contact / (insole_length - 1)
        )

        fmg_index = round(
            relative_position
            * (fmg_length - 1)
        )

        mapped_contacts.append(fmg_index)

    return mapped_contacts


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


print("\n" + "=" * 60)
print("CONTACTS MAPPED TO FMG")
print("=" * 60)

print("Left FMG contacts:")
print(left_fmg_contacts)

print("\nRight FMG contacts:")
print(right_fmg_contacts)

# ============================================================
# CREATE INDIVIDUAL GAIT CYCLES
# ============================================================

def create_gait_cycles(
    fmg_trial,
    mapped_contacts,
    side
):

    cycles = []

    if side == "left":

        channel_columns = [
            f"left_ch{i}"
            for i in range(1, 9)
        ]

    else:

        channel_columns = [
            f"right_ch{i}"
            for i in range(1, 9)
        ]


    for i in range(
        len(mapped_contacts) - 1
    ):

        start = mapped_contacts[i]
        end = mapped_contacts[i + 1]

        cycle = (
            fmg_trial
            .iloc[start:end]
            [channel_columns]
            .copy()
        )

        cycle = cycle.reset_index(
            drop=True
        )

        cycles.append(cycle)

    return cycles


left_cycles = create_gait_cycles(
    fmg_trial,
    left_fmg_contacts,
    "left"
)

right_cycles = create_gait_cycles(
    fmg_trial,
    right_fmg_contacts,
    "right"
)


print("\n" + "=" * 60)
print("GAIT CYCLES CREATED")
print("=" * 60)

print(
    "Left gait cycles:",
    len(left_cycles)
)

print(
    "Right gait cycles:",
    len(right_cycles)
)

print("\nLeft cycle lengths:")

print([
    len(cycle)
    for cycle in left_cycles
])

print("\nRight cycle lengths:")

print([
    len(cycle)
    for cycle in right_cycles
])

# ============================================================
# VISUALISE SEGMENTED FMG CYCLES
# ============================================================

fig, axes = plt.subplots(
    2,
    1,
    figsize=(14, 8)
)


# Plot first 3 left gait cycles
for i, cycle in enumerate(
    left_cycles[:3]
):

    normalized_x = np.linspace(
        0,
        100,
        len(cycle)
    )

    axes[0].plot(
        normalized_x,
        cycle["left_ch1"],
        label=f"Cycle {i + 1}"
    )


axes[0].set_title(
    "Left FMG - First 3 Segmented Gait Cycles"
)

axes[0].set_xlabel(
    "Gait Cycle (%)"
)

axes[0].set_ylabel(
    "FMG Amplitude"
)

axes[0].legend()

axes[0].grid(True)


# Plot first 3 right gait cycles
for i, cycle in enumerate(
    right_cycles[:3]
):

    normalized_x = np.linspace(
        0,
        100,
        len(cycle)
    )

    axes[1].plot(
        normalized_x,
        cycle["right_ch1"],
        label=f"Cycle {i + 1}"
    )


axes[1].set_title(
    "Right FMG - First 3 Segmented Gait Cycles"
)

axes[1].set_xlabel(
    "Gait Cycle (%)"
)

axes[1].set_ylabel(
    "FMG Amplitude"
)

axes[1].legend()

axes[1].grid(True)


plt.tight_layout()

plt.show()