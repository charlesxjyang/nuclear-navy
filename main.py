import pandas as pd

df = pd.read_table("data/nuclear_reactors.txt",delimiter=',')
print(df.head())

print(df.columns)

df['Commercial operation'] = pd.to_datetime(df['Commercial operation'],dayfirst=True)

print(df['Commercial operation'].dt.strftime('%Y'))