from pathlib import Path

from src.data_loader import read_insole_file


# ============================================================
# SELECT SUBJECT
# ============================================================

subject = Path("Sub01_H")


# ============================================================
# LEFT AND RIGHT INSOLE FILES
# ============================================================

left_file = subject / "abh_1L"
right_file = subject / "abh_1R"


print("Left file:", left_file)
print("Left exists:", left_file.exists())

print("Right file:", right_file)
print("Right exists:", right_file.exists())


# ============================================================
# LOAD LEFT INSOLE
# ============================================================

left_df = read_insole_file(left_file)

print("\n================ LEFT INSOLE ================")

print("Shape:", left_df.shape)

print("\nColumns:")
print(left_df.columns.tolist())

print("\nFirst 5 rows:")
print(left_df.head())


# ============================================================
# LOAD RIGHT INSOLE
# ============================================================

right_df = read_insole_file(right_file)

print("\n================ RIGHT INSOLE ================")

print("Shape:", right_df.shape)

print("\nColumns:")
print(right_df.columns.tolist())

print("\nFirst 5 rows:")
print(right_df.head())


print("\n================ TRIGGER CHECK ================")

print("\nLEFT trigger values:")
print(left_df["trigger"].value_counts().sort_index())

print("\nRIGHT trigger values:")
print(right_df["trigger"].value_counts().sort_index())

print("\nLEFT time range:")
print(left_df["time"].min(), "to", left_df["time"].max())

print("\nRIGHT time range:")
print(right_df["time"].min(), "to", right_df["time"].max())

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


left_regions = find_trigger_regions(left_df)
right_regions = find_trigger_regions(right_df)

print("\n================ TRIGGER REGIONS ================")

print("LEFT trigger regions:", len(left_regions))
print("RIGHT trigger regions:", len(right_regions))

print("\nFirst 5 LEFT regions:")
print(left_regions[:5])

print("\nFirst 5 RIGHT regions:")
print(right_regions[:5])