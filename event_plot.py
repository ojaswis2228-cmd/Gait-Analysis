import pandas as pd
import matplotlib.pyplot as plt



rows = []

with open("Sub01_H/abh_1.txt", "r", encoding="utf-8", errors="ignore") as f:

    next(f)   # Skip first line

    for line in f:

        parts = line.split()

        if len(parts) != 18:
            continue

        try:
            rows.append([float(x) for x in parts])
        except:
            continue



columns = [
    "Time",
    "Trigger",
    "L1","L2","L3","L4","L5","L6","L7","L8",
    "R1","R2","R3","R4","R5","R6","R7","R8"
]

df = pd.DataFrame(rows, columns=columns)

print("Dataset Shape :", df.shape)

# -----------------------------
# FIRST TRIGGER
# -----------------------------

event = 609          # First trigger

window = 300         # Samples before and after

start = event - window
end = event + window

# -----------------------------
# PLOT LEFT CHANNELS
# -----------------------------

left_channels = [
    "L1","L2","L3","L4",
    "L5","L6","L7","L8"
]

plt.figure(figsize=(16,8))

for ch in left_channels:
    plt.plot(df[ch][start:end].values, label=ch)

plt.axvline(window,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Trigger")

plt.title("Left FMG Channels Around First Trigger")
plt.xlabel("Samples")
plt.ylabel("FMG Amplitude")
plt.grid(True)
plt.legend()

plt.show()

# -----------------------------
# PLOT RIGHT CHANNELS
# -----------------------------

right_channels = [
    "R1","R2","R3","R4",
    "R5","R6","R7","R8"
]

plt.figure(figsize=(16,8))

for ch in right_channels:
    plt.plot(df[ch][start:end].values, label=ch)

plt.axvline(window,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Trigger")

plt.title("Right FMG Channels Around First Trigger")
plt.xlabel("Samples")
plt.ylabel("FMG Amplitude")
plt.grid(True)
plt.legend()

plt.show()