from pathlib import Path

from src.data_loader import read_fmg_file


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

left_df = read_fmg_file(left_file)

print("\n================ LEFT INSOLE ================")

print("Shape:", left_df.shape)

print("\nColumns:")
print(left_df.columns.tolist())

print("\nFirst 5 rows:")
print(left_df.head())


# ============================================================
# LOAD RIGHT INSOLE
# ============================================================

right_df = read_fmg_file(right_file)

print("\n================ RIGHT INSOLE ================")

print("Shape:", right_df.shape)

print("\nColumns:")
print(right_df.columns.tolist())

print("\nFirst 5 rows:")
print(right_df.head())