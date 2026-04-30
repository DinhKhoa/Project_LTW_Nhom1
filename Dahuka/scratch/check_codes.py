import pandas as pd
import os

df = pd.read_excel("Sanpham.xlsx")
print("Unique MaDMSP:", df['MaDMSP'].unique().tolist())
print("Sample MaSP:", df['MaSP'].head().tolist())
