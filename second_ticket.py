import pandas as pd

file_path = r"C:\JP\Developer\PERSONAL\Data-Analytics-Job-Simulation\urbankart_cleaning\urbankart_sales_clean.csv"

df = pd.read_csv(file_path)

print(df.head())
print(df.columns)
print(df.shape)
