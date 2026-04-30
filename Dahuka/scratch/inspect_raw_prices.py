import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('Sanpham.xlsx')
for index, row in df.iterrows():
    print(f"SKU: {row.get('MaSP')}, Name: {row.get('TenSP')}, Raw Price: '{row.get('Gia')}'")
