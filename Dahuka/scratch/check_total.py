import pandas as pd
df1 = pd.read_excel('Sanpham.xlsx')
df2 = pd.read_excel('hinhanhsanpham.xlsx')
print(f"Sanpham.xlsx rows: {len(df1)}")
print(f"hinhanhsanpham.xlsx rows: {len(df2)}")
