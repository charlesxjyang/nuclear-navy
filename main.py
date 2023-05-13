import pandas as pd
from datetime import timedelta, datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

#preprocessing for the nuclear navy data

classes = ['SSN', 'SSBN', 'CGN_CVN_DSRV']

all_reactors = pd.read_csv("data/reactor_sizes.txt")
all_reactors['Output (MWe)'] = all_reactors['Output (MWe)'].astype(float)
reactor_lookup = dict(
  zip(all_reactors['Reactor'], all_reactors['Output (MWe)']))
final_df = []


def process_datetime_col(df: pd.DataFrame, col: str):
  df[col] = pd.to_datetime(df[col], errors='coerce')
  future_dates = df[col].dt.year > datetime.now().year
  df.loc[future_dates, col] -= timedelta(days=365.25 * 100)
  return df


for c in classes:
  ships, reactors = pd.read_csv("data/" + c + ".txt",
                                index_col=None), pd.read_csv("data/" + c +
                                                             "_reactor.txt")
  new_df = pd.merge(ships, reactors, on='Hull Nr.')
  process_datetime_col(new_df, r"Comm'd")
  process_datetime_col(new_df, 'Launched')
  process_datetime_col(new_df, 'Keel Laid')

  new_df = new_df.dropna(subset=[r"Comm'd"])
  new_df["Year_Comm"] = new_df[r"Comm'd"].dt.strftime('%Y')
  new_df["Year_Launched"] = new_df['Launched'].dt.strftime('%Y')
  new_df["Year_Keel"] = new_df['Keel Laid'].dt.strftime('%Y')
  new_df['Nr. Reactor'] = pd.to_numeric(new_df['Nr. Reactor'],
                                        errors='coerce').dropna()
  new_df[['Reactor']] = new_df[['Reactor']].applymap(lambda x: x.strip())
  new_df['Total MW'] = new_df['Nr. Reactor'] * new_df['Reactor'].map(
    reactor_lookup)
  new_df = new_df.dropna(subset=["Total MW"])
  final_df.append(new_df)
naval_df = pd.concat(final_df)

# preprocessing for the civilian nuclear reactor fleet
df = pd.read_table("data/nuclear_reactors.txt", delimiter=',')
df = df[(df['Status'] != 'Planned') & (df['Status'] != 'Under commissioning') &
        (df['Status'] != 'Under construction')]

df['Commercial operation'] = pd.to_datetime(df['Commercial operation'],
                                            dayfirst=True,
                                            format='mixed')
df['Year_Commercial'] = df['Commercial operation'].dt.strftime('%Y')

df['Construction start'] = pd.to_datetime(df['Construction start'],
                                          dayfirst=True,
                                          format='mixed')
df['Year_Construction'] = df['Construction start'].dt.strftime('%Y')

df['Diff'] = df['Commercial operation'] - df['Construction start']
df['Year_Diff'] = df['Diff'] / pd.Timedelta(days=365.25)

naval_df['Diff'] = naval_df[r"Comm'd"] - naval_df['Keel Laid']
naval_df['Year_Diff'] = naval_df['Diff'] / pd.Timedelta(days=365.25)


def plot(navy_col="Year_Comm", civilian_col="Year_Commercial"):
  subset_df = df[[civilian_col, 'Net capacity (MW)']]
  subset_df = subset_df.groupby(civilian_col).sum(
    "Net capacity (MW)").reset_index()
  naval_reactors = naval_df[[navy_col, 'Total MW']]
  naval_reactors = naval_reactors.groupby(navy_col).sum(
    "Total MW").reset_index()

  ## Plotting

  # ensure 'year' column is of type int
  naval_reactors[navy_col] = naval_reactors[navy_col].astype(int)
  subset_df[civilian_col] = subset_df[civilian_col].astype(int)

  # find the range of years to include in both dataframes
  all_years = set(naval_reactors[navy_col]).union(subset_df[civilian_col])

  # reindex the dataframes to include all years and fill missing amounts with 0
  naval_reactors.set_index(navy_col, inplace=True)
  naval_reactors = naval_reactors.reindex(all_years, fill_value=0.0)

  subset_df.set_index(civilian_col, inplace=True)
  subset_df = subset_df.reindex(all_years, fill_value=0.0)

  # reset index
  naval_reactors.reset_index(inplace=True)
  subset_df.reset_index(inplace=True)

  # sort dataframes by year
  naval_reactors.sort_values(navy_col, inplace=True)
  subset_df.sort_values(civilian_col, inplace=True)

  # plot
  fig, ax = plt.subplots()

  width = 0.5  # the width of the bars]
  # replace zero with nan to prevent line graph from dropping
  naval_reactors.loc[naval_reactors['Total MW'] == 0.0, 'Total MW'] = np.nan
  ax.plot(naval_reactors[navy_col],
          naval_reactors["Total MW"],
          label='Navy',
          color='orange')
  # ax.plot(subset_df['Year'], subset_df['Net capacity (MW)'], label='Civilian')
  # rects1 = ax.bar(naval_reactors['Year'],
  #                 naval_reactors["Total MW"],
  #                 width,
  #                 label='Navy', alpha=0.7)
  rects2 = ax.bar(subset_df[civilian_col],
                  subset_df["Net capacity (MW)"],
                  width,
                  label='Civilian Fleet',
                  alpha=0.7)

  ax.set_xlabel('Year')
  ax.set_yscale("log", nonpositive='clip')
  ax.set_ylabel('Nameplate Nuclear Capacity Installed (MW)')
  ax.set_title('Nuclear Reactors in US, 1952-2015')
  ax.legend()

  plt.savefig("graph.png")


plot("Year_Keel", civilian_col='Year_Construction')


def plot_construction(navy_col="Year_Comm", civilian_col="Year_Commercial"):
  subset_df = df[[civilian_col, 'Year_Diff']]
  subset_df = subset_df.groupby(civilian_col).mean('Year_Diff').reset_index()
  naval_reactors = naval_df[[navy_col, 'Year_Diff']]
  naval_reactors = naval_reactors.groupby(navy_col).mean(
    'Year_Diff').reset_index()

  ## Plotting

  # ensure 'year' column is of type int
  naval_reactors[navy_col] = naval_reactors[navy_col].astype(int)
  subset_df[civilian_col] = subset_df[civilian_col].astype(int)

  # find the range of years to include in both dataframes
  all_years = set(naval_reactors[navy_col]).union(subset_df[civilian_col])

  # reindex the dataframes to include all years and fill missing amounts with 0
  naval_reactors.set_index(navy_col, inplace=True)
  naval_reactors = naval_reactors.reindex(all_years, fill_value=0.0)

  subset_df.set_index(civilian_col, inplace=True)
  subset_df = subset_df.reindex(all_years, fill_value=0.0)

  # reset index
  naval_reactors.reset_index(inplace=True)
  subset_df.reset_index(inplace=True)

  # sort dataframes by year
  naval_reactors.sort_values(navy_col, inplace=True)
  subset_df.sort_values(civilian_col, inplace=True)

  # plot
  fig, ax = plt.subplots()

  width = 0.5  # the width of the bars]
  # replace zero with nan to prevent line graph from dropping
  naval_reactors.loc[naval_reactors['Year_Diff'] == 0.0, 'Year_Diff'] = np.nan
  ax.plot(naval_reactors[navy_col],
          naval_reactors['Year_Diff'],
          label='Navy',
          color='orange')
  # ax.plot(subset_df['Year'], subset_df['Net capacity (MW)'], label='Civilian')
  # rects1 = ax.bar(naval_reactors['Year'],
  #                 naval_reactors["Total MW"],
  #                 width,
  #                 label='Navy', alpha=0.7)
  rects2 = ax.bar(subset_df[civilian_col],
                  subset_df['Year_Diff'],
                  width,
                  label='Civilian Fleet',
                  alpha=0.7)

  ax.set_xlabel('Year')
  #ax.set_yscale("log", nonpositive='clip')
  ax.set_ylabel('Construction Time')
  ax.set_title('Nuclear Reactors in US, 1952-2015')
  ax.legend()

  plt.savefig("graph_construction.png")


plot_construction()
