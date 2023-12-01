"""Utilities for visualizations."""
import pandas as pd
import copy
import seaborn as sns
import numpy as np

def correlation_histogram(dataframe: pd.DataFrame, bins = 'auto', clusters = None, ax = None) -> None:
  """
  Parameters
  ----------
  - df: pandas.DataFrame

  Returns
  -------
  None

  Prints out Correlation histogram without autocorrelations or repetitions
  """
  df = copy.deepcopy(dataframe)
    
  if df.columns.nlevels > 1:
    df = df.droplevel('Industry',axis=1)
  
  corrs = np.tril(df.corr().values, -1)

  if clusters == None:
    corrs = corrs[corrs.nonzero()]
    sns.histplot(corrs, bins = bins)

  else:
    # this code is a bit of spaghetti, and I apologize for it
    pairs = {}
    for i in range(df.shape[1]):
        for j in range(i):
            col1, col2 = df.columns[i], df.columns[j]
            pairs[col1 + '+' + col2] = [corrs[i][j], 1*(clusters[col1] == clusters[col2])]

    pairs_df = pd.DataFrame.from_dict(pairs, 
                                      orient='index', 
                                      columns = ["correlation", "Together"])

    pairs_df["Together"] = pairs_df["Together"].replace({1 : "Together", 0 : "Not Together"})

    sns.histplot(data = pairs_df,
             bins = bins,
             x="correlation", 
             hue="Together", 
             hue_order = ["Not Together", "Together"],
             multiple="stack",
             ax = ax)
  return None