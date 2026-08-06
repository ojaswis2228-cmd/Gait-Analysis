with open("Sub01_H/abh_1L", "r", encoding="utf-8", errors="ignore") as f:

    print("="*70)
    print("FIRST 50 LINES OF abh_1L")
    print("="*70)

    for i in range(50):

        line = f.readline()

        if not line:
            break

        print(f"Line {i+1}:")
        print(repr(line))
        print("Split =", line.split())
        print("Columns =", len(line.split()))
        print("-"*70)