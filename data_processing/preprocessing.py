"""Utilities to process the loaded data."""

import pandas as pd
import seaborn as sns
import numpy as np
from typing import Dict, Callable
import copy

def normalized(series : pd.Series, norm : Callable) -> pd.Series:
    """
    Parameters
    ----------
    - series: pandas.Series
        The Pandas series for which the norms will be computed.
    - norm: Callable
        The norm function to be used.

    Returns
    -------
        The same series with the entries normalized according the chosen norm.
    """

    series_c = copy.deepcopy(series)

    norms = pd.Series(norm(num) for num in series_c)

    return series_c.divide(norms)

def risk(df: pd.DataFrame, window = 10) -> pd.DataFrame:
  """
  Parameters
  ----------
  - df: pandas.DataFrame
      The Pandas dataframe whose columns are returns of assets
  - window: int
      The size of sliding window used to compute the risk

  Returns
  -------
      A dataframe whose columns correspond to the asset risk at each time, 
      computed using a sample standard deviation on a sliding window. 
  """
  return df.rolling(window).std()*np.sqrt(window/(window-1))

def sharpe_normalize(df: pd.DataFrame, window = None) -> pd.DataFrame:
  """
  Parameters
  ----------
  - df: pandas.DataFrame
      The Pandas dataframe which should be normalized by Sharpe ratio. 
      df should be a dataframe whose columns are time series
  - window: int
      The size of sliding window used to compute the risk

  Returns
  -------
      A dataframe of series normalized by the Sharpe ratio. If 
      p_t are the entries in one series, then define:
        - r(t) = p(t+1) / p(t)
        - sigma(t) = the standard variation of r(t) at time t
        - r_f(t) = risk-free rate = mean over all columns of r(t)
        - Sharpe_t = (r(t) - r_f(t)) / sigma(t)
      To estimate sigma(t), we use a sliding window around t. If window 
      is None, then we estimate sigma as a constant.

      Warning: the returned dataframe is (window) + 1 entries shorter than 
      the input series, or 1 entry shorter if window is None
  """

  df_c = copy.deepcopy(df)
  ROR = df_c.pct_change().dropna()

  if window == None:
    sigma = ROR.std()
    sharpe = ROR.sub(ROR.mean(axis = 1), axis = 0)/sigma
    return sharpe
  elif isinstance(window, int) and window > 0:
    sigma = risk(ROR, window)
    sharpe = (ROR.sub(ROR.mean(axis = 1), axis = 0)/sigma).dropna()
    return sharpe
  else:
    print("Window needs to be an integer, or None for constant risk estimate")
    return None

def l2_normalization(dataframe: pd.DataFrame) -> pd.DataFrame:
  """
  Parameters
  ----------
  - df: pandas.DataFrame
      The Pandas dataframe which should be normalized by the L^2 
      norm

  Returns
  -------
  Normalized dataframe
  """

  dfn = copy.deepcopy(dataframe)
  for ticker in dfn:
    dfn[ticker] = dfn[ticker]/np.linalg.norm(dfn[ticker])
  return dfn

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
