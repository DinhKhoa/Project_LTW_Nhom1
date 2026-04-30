import pandas as pd

def inspect_excel(filename):
    print(f"--- Inspecting {filename} ---")
    try:
        df = pd.read_excel(filename)
        print("Columns:", df.columns.tolist())
        print("First 5 rows:")
        print(df.head())
        print("\n")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

inspect_excel("Sanpham.xlsx")
inspect_excel("hinhanhsanpham.xlsx")
