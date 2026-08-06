import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# STEP 1 : LOAD DATA
# =====================================================

rows = []

with open("Sub01_H/abh_1.txt", "r", encoding="utf-8", errors="ignore") as f:

    next(f)  # Skip metadata line

    for line in f:

        parts = line.split()

        # Keep only valid rows
        if len(parts) != 18:
            continue

        try:
            parts = [float(x) for x in parts]
            rows.append(parts)

        except ValueError:
            continue

# =====================================================
# STEP 2 : CREATE DATAFRAME
# =====================================================

df = pd.DataFrame(rows)

df.columns = [
    "Time",
    "Trigger",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L7",
    "L8",
    "R1",
    "R2",
    "R3",
    "R4",
    "R5",
    "R6",
    "R7",
    "R8",
]

# =====================================================
# STEP 3 : BASIC INFORMATION
# =====================================================

print("=" * 60)
print("DATASET SHAPE")
print(df.shape)

print("=" * 60)
print("FIRST 5 ROWS")
print(df.head())

print("=" * 60)
print("DATASET INFO")
print(df.info())

print("=" * 60)
print("COLUMN STATISTICS")

for i in range(len(df.columns)):

    print(
        f"{df.columns[i]} : "
        f"Min = {df.iloc[:,i].min()} | "
        f"Max = {df.iloc[:,i].max()} | "
        f"Unique = {df.iloc[:,i].nunique()}"
    )

# =====================================================
# STEP 4 : TRIGGER ANALYSIS
# =====================================================

print("=" * 60)
print("TRIGGER VALUE COUNT")

print(df["Trigger"].value_counts())

trigger_index = df.index[df["Trigger"] == 1]

print("=" * 60)
print("FIRST 50 TRIGGER POSITIONS")

print(trigger_index[:50])

# =====================================================
# STEP 5 : PLOT TRIGGER
# =====================================================

plt.figure(figsize=(15,3))

plt.plot(df["Trigger"])

plt.title("Trigger Signal")

plt.xlabel("Samples")

plt.ylabel("Trigger")

plt.grid(True)

plt.show()

# =====================================================
# STEP 6 : PLOT LEFT CHANNEL 1
# =====================================================

plt.figure(figsize=(15,5))

plt.plot(df["L1"])

plt.title("Left FMG Channel 1")

plt.xlabel("Samples")

plt.ylabel("Amplitude")

plt.grid(True)

plt.show()

# =====================================================
# STEP 7 : PLOT ALL LEFT FMG CHANNELS
# =====================================================

plt.figure(figsize=(18,8))

for col in ["L1","L2","L3","L4","L5","L6","L7","L8"]:

    plt.plot(df[col][:3000], label=col)

plt.legend()

plt.title("Left FMG Channels (First 3000 Samples)")

plt.grid(True)

plt.show()