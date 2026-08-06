import pandas as pd

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

cols = [
    "Time","Trigger",
    "L1","L2","L3","L4","L5","L6","L7","L8",
    "R1","R2","R3","R4","R5","R6","R7","R8"
]

df = pd.DataFrame(rows, columns=cols)

trigger = df["Trigger"]

inside = False
start = None

print("Trigger Blocks")
print("-"*40)

for i, val in enumerate(trigger):

    if val == 1 and not inside:
        start = i
        inside = True

    elif val == 0 and inside:
        end = i - 1
        print(f"Start = {start:6d}  End = {end:6d}  Length = {end-start+1}")
        inside = False

if inside:
    print(f"Start = {start:6d}  End = {len(trigger)-1:6d}")