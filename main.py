from pathlib import Path

import matplotlib.pyplot as plt

from src.data_loader import read_fmg_file


# ============================================================
# 1. PROJECT / DATASET PATH
# ============================================================

DATA_DIR = Path(".")


# ============================================================
# 2. SELECT ONE SUBJECT AND ONE FMG FILE
# ============================================================

subject = DATA_DIR / "Sub01_H"

fmg_file = subject / "abh_1.txt"


print("Subject:", subject)
print("FMG file:", fmg_file)
print("File exists:", fmg_file.exists())


# ============================================================
# 3. LOAD THE FMG DATA
# ============================================================

df = read_fmg_file(fmg_file)


print("\nData loaded successfully!")

print("Shape:", df.shape)


# ============================================================
# 4. SHOW COLUMNS
# ============================================================

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 5. SHOW FIRST 5 ROWS
# ============================================================

print("\nFirst 5 rows:")
print(df.head())


# ============================================================
# 6. CHECK UNIQUE TRIGGER VALUES
# ============================================================

print("\nUnique trigger values:")
print(sorted(df["trigger"].unique()))


# ============================================================
# 7. COUNT TRIGGER VALUES
# ============================================================

print("\nTrigger counts:")
print(df["trigger"].value_counts().sort_index())


# ============================================================
# 8. FIND ALL TRIGGER = 1 REGIONS
# ============================================================

print("\nTrigger = 1 regions:")

trigger = df["trigger"].values

in_event = False
start = None

for i, value in enumerate(trigger):

    if value == 1 and not in_event:

        start = i
        in_event = True

    elif value == 0 and in_event:

        end = i - 1

        start_time_event = df.iloc[start]["time"]
        end_time_event = df.iloc[end]["time"]

        print(
            f"Samples: {start} - {end} | "
            f"Time: {start_time_event:.2f} - {end_time_event:.2f} sec | "
            f"Duration: {end_time_event - start_time_event:.2f} sec"
        )

        in_event = False


if in_event:

    end = len(trigger) - 1

    start_time_event = df.iloc[start]["time"]
    end_time_event = df.iloc[end]["time"]

    print(
        f"Samples: {start} - {end} | "
        f"Time: {start_time_event:.2f} - {end_time_event:.2f} sec | "
        f"Duration: {end_time_event - start_time_event:.2f} sec"
    )

print("\nTime between trigger events:")

trigger_times = []

trigger = df["trigger"].values

in_event = False

for i, value in enumerate(trigger):

    if value == 1 and not in_event:

        trigger_times.append(df.iloc[i]["time"])
        in_event = True

    elif value == 0 and in_event:

        in_event = False


for i in range(1, len(trigger_times)):

    difference = trigger_times[i] - trigger_times[i - 1]

    print(
        f"Event {i}: "
        f"{difference:.2f} seconds"
    )




# ============================================================
# 9. ZOOM INTO THE BEGINNING OF THE RECORDING
# ============================================================

start_time = 240
end_time = 450


zoom_df = df[
    (df["time"] >= start_time) &
    (df["time"] <= end_time)
]


# ============================================================
# 10. CREATE FMG + TRIGGER GRAPH
# ============================================================

fig, (ax1, ax2) = plt.subplots(
    2,
    1,
    figsize=(16, 8),
    sharex=True
)


# ------------------------------------------------------------
# TOP: FMG SIGNAL
# ------------------------------------------------------------

ax1.plot(
    zoom_df["time"],
    zoom_df["left_ch1"]
)

ax1.set_ylabel("FMG Amplitude")

ax1.set_title(
    "FMG Signal - Sub01_H / abh_1 - Zoomed"
)

ax1.grid(True)


# ------------------------------------------------------------
# BOTTOM: TRIGGER SIGNAL
# ------------------------------------------------------------

ax2.plot(
    zoom_df["time"],
    zoom_df["trigger"]
)

ax2.set_xlabel("Time (seconds)")

ax2.set_ylabel("Trigger")

ax2.set_ylim(-0.1, 1.1)

ax2.set_title("Trigger - Zoomed")

ax2.grid(True)


# ============================================================
# 11. DISPLAY GRAPH
# ============================================================

plt.tight_layout()

plt.show()

# ============================================================
# 12. INSPECT THE FIRST TRIAL
# ============================================================

trial_start = 275
trial_end = 305

trial_df = df[
    (df["time"] >= trial_start) &
    (df["time"] <= trial_end)
]

fig, (ax1, ax2) = plt.subplots(
    2,
    1,
    figsize=(16, 8),
    sharex=True
)

# FMG
ax1.plot(
    trial_df["time"],
    trial_df["left_ch1"]
)

ax1.set_ylabel("FMG Amplitude")
ax1.set_title("First Trial - Left FMG Channel 1")
ax1.grid(True)

# Trigger
ax2.plot(
    trial_df["time"],
    trial_df["trigger"]
)

ax2.set_xlabel("Time (seconds)")
ax2.set_ylabel("Trigger")
ax2.set_ylim(-0.1, 1.1)
ax2.set_title("First Trial - Trigger")
ax2.grid(True)

plt.tight_layout()
plt.show()


# ============================================================
# 13. CREATE TRIALS FROM TRIGGER PAIRS
# ============================================================

trigger_times = []

trigger = df["trigger"].values

in_event = False

for i, value in enumerate(trigger):

    if value == 1 and not in_event:

        trigger_times.append(df.iloc[i]["time"])
        in_event = True

    elif value == 0 and in_event:

        in_event = False


print("\n" + "=" * 60)
print("TRIALS DETECTED")
print("=" * 60)

trial_number = 1

for i in range(0, len(trigger_times) - 1, 2):

    trial_start = trigger_times[i]
    trial_end = trigger_times[i + 1]

    duration = trial_end - trial_start

    print(
        f"Trial {trial_number}: "
        f"{trial_start:.2f} → {trial_end:.2f} sec "
        f"({duration:.2f} sec)"
    )

    trial_number += 1