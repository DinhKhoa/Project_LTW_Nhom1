import pandas as pd
import sys

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_excel('Sanpham.xlsx')
    print("Columns:", df.columns.tolist())
    print(f"Total rows in Excel: {len(df)}")
    print("Rows with missing or 0 price:")
    for index, row in df.iterrows():
        price = row.get('Gia')
        if pd.isna(price) or price == 0 or str(price).strip() == '0' or str(price).strip() == '':
            print(f"{row.get('MaSP')}: {row.get('TenSP')} - {price}")
except Exception as e:
    print(f"Error: {e}")
