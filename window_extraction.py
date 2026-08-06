import pandas as pd
import numpy as np

# -----------------------------
# LOAD DATA
# -----------------------------

rows = []

with open("Sub01_H/abh_1.txt", "r", encoding="utf-8", errors="ignore") as f:

    next(f)

    for line in f:

        parts = line.split()

        if len(parts) != 18:
            continue

        try:
            rows.append([float(x) for x in parts])
        except:
            continue

df = pd.DataFrame(rows)

df.columns = [
    "Time",
    "Trigger",
    "L1","L2","L3","L4","L5","L6","L7","L8",
    "R1","R2","R3","R4","R5","R6","R7","R8"
]

# -----------------------------
# FIND TRIGGER BLOCKS
# -----------------------------

trigger = df["Trigger"].values

starts = []

inside = False

for i, value in enumerate(trigger):

    if value == 1 and not inside:
        starts.append(i)
        inside = True

    elif value == 0:
        inside = False


print("="*60)
print("Total Trigger Events :", len(starts))
print("="*60)

print(starts)

# -----------------------------
# EXTRACT WINDOWS
# -----------------------------

WINDOW = 300

windows = []

for s in starts:

    if s-WINDOW < 0:
        continue

    if s+WINDOW >= len(df):
        continue

    temp = df.iloc[s-WINDOW:s+WINDOW]

    windows.append(temp)

print()
print("Windows Extracted :", len(windows))

print()

print("One Window Shape")

print(windows[0].shape)