import numpy as np
import pandas as pd

classes = ['SSN', 'SSBN', 'CGN_CVN_DSRV']

all_reactors = pd.read_csv("data/reactor_sizes.txt")
all_reactors['Output (MWe)'] = all_reactors['Output (MWe)'].astype(float)
reactor_lookup = dict(
  zip(all_reactors['Reactor'], all_reactors['Output (MWe)']))
final_df = []
for c in classes:
  print(c)
  ships, reactors = pd.read_csv("data/" + c + ".txt",
                                index_col=None), pd.read_csv("data/" + c +
                                                             "_reactor.txt")
  new_df = pd.merge(ships, reactors, on='Hull Nr.')
  new_df[r"Comm'd"] = pd.to_datetime(new_df[r"Comm'd"], errors='coerce') #fix Y2K issues
  new_df[["Comm'd"] = new_df[["Comm'd"]].applymap(lambda x: if x.year>2020 then x.year -100)
  new_df = new_df.dropna(subset=[r"Comm'd"])
  new_df["Year"] = new_df[r"Comm'd"].dt.strftime('%Y')
  new_df['Nr. Reactor'] = pd.to_numeric(new_df['Nr. Reactor'],
                                        errors='coerce').dropna()
  new_df[['Reactor']] = new_df[['Reactor']].applymap(lambda x: x.strip())
  new_df['Total MW'] = new_df['Nr. Reactor'] * new_df['Reactor'].map(
    reactor_lookup)
  new_df = new_df.dropna(subset=["Total MW"])
  final_df.append(new_df)
naval_df = pd.concat(final_df)