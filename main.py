import pandas as pd

df = pd.read_table("data/nuclear_reactors.txt", delimiter=',')
df = df[(df['Status'] != 'Planned') & (df['Status'] != 'Under commissioning') &
        (df['Status'] != 'Under construction')]

df['Commercial operation'] = pd.to_datetime(df['Commercial operation'],
                                            dayfirst=True,
                                            format='mixed')

print(df['Commercial operation'].dt.strftime('%Y'))
df['Year'] = df['Commercial operation'].dt.strftime('%Y')
subset_df = df[['Year','Net capacity (MW)']]

print(subset_df.groupby('Year')['Net capacity (MW)'].sum().reset_index())


