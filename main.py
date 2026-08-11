from pathlib import Path
import matplotlib.pyplot as plt

from src.data_loader import read_fmg_file


# Project folder
DATA_DIR = Path(".")


# Select one subject
subject = DATA_DIR / "Sub01_H"


# Select FMG file
fmg_file = subject / "abh_1.txt"


print("Reading:", fmg_file)


# Read the FMG data
df = read_fmg_file(fmg_file)


print("\nData loaded successfully!")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())
print("\nUnique trigger values:")
print(sorted(df["trigger"].unique()))

print("\nTrigger counts:")
print(df["trigger"].value_counts().sort_index())


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

        print(
            f"Start: {start}, "
            f"End: {end}, "
            f"Samples: {end - start + 1}"
        )

        in_event = False

# Handle event if file ends while trigger is 1
if in_event:
    end = len(trigger) - 1

    print(
        f"Start: {start}, "
        f"End: {end}, "
        f"Samples: {end - start + 1}"
    )



    import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(16, 8),
    sharex=True
)

# -----------------------------
# FMG signal
# -----------------------------
ax1.plot(
    df["time"],
    df["left_ch1"]
)

ax1.set_ylabel("FMG Amplitude")
ax1.set_title("FMG Signal – Sub01_H / abh_1")
ax1.grid(True)


# -----------------------------
# Trigger signal
# -----------------------------
ax2.plot(
    df["time"],
    df["trigger"]
)

ax2.set_xlabel("Time (seconds)")
ax2.set_ylabel("Trigger")
ax2.set_title("Trigger Signal")
ax2.set_ylim(-0.1, 1.1)
ax2.grid(True)


plt.tight_layout()
plt.show()