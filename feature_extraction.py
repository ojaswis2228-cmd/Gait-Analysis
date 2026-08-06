import pandas as pd
import numpy as np

# --------------------
# LOAD DATA
# --------------------

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
    "Time","Trigger",
    "L1","L2","L3","L4","L5","L6","L7","L8",
    "R1","R2","R3","R4","R5","R6","R7","R8"
]

# --------------------
# FIND TRIGGER STARTS
# --------------------

starts = []

inside = False

for i, v in enumerate(df["Trigger"]):

    if v == 1 and not inside:
        starts.append(i)
        inside = True

    elif v == 0:
        inside = False

WINDOW = 300

feature_rows = []

for s in starts:

    if s-WINDOW < 0:
        continue

    if s+WINDOW >= len(df):
        continue

    window = df.iloc[s-WINDOW:s+WINDOW]

    features = []

    # Skip Time and Trigger
    for col in df.columns[2:]:

        signal = window[col]

        features.append(signal.mean())
        features.append(signal.std())
        features.append(signal.var())
        features.append(signal.min())
        features.append(signal.max())
        features.append(np.sqrt(np.mean(signal**2)))

    feature_rows.append(features)

feature_df = pd.DataFrame(feature_rows)

print("="*60)
print("Feature Matrix Shape")
print(feature_df.shape)

print()

print(feature_df.head())