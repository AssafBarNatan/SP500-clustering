"""Utilities to process the loaded data."""

import pandas as pd
import numpy as np
import copy
from inspect import signature
from functools import partial
from functools import reduce
from typing import Dict, Callable
from data_pipeline.retrieval import DataBank

def normalize(df : pd.Series, norm : Callable = np.linalg.norm) -> pd.Series:
    """
    Parameters
    ----------
    - df: pandas.DataFrame
      The Pandas dataframe to be normalized.
    - norm: Callable
        The norm function to be used. (The l2-norm from numpy.linalg, by default.)

    Returns
    -------
    - df_norm: pandas.DataFrame
        The same dataframe with all its values normalized.
    """
    df_norm = df.dropna(axis = 1, inplace=True)

    df_norm = df.apply(lambda x : x / norm(x), result_type='broadcast')

    return df_norm

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

def market_adjust(df: pd.DataFrame) -> pd.DataFrame:
  """
  Parameters
  ----------
  - df: pandas.DataFrame

  Returns
  -------
  - df: pandas.DataFrame of market adjusted returns

  """
  df_c = copy.deepcopy(df)
  
  return df_c.sub(df.mean(axis = 1), axis = 0)

def industry_adjust(df: pd.DataFrame, ticker_to_sector_dict = DataBank().ticker_to_sector_map()) -> pd.DataFrame:
  """
  Parameters
  ----------
  - df: pandas.DataFrame
  - clusters: list

  Returns
  -------
  - df: pandas.DataFrame of industry adjusted returns

  If df has two layers of column indices. The first should be the cluster labels 
  and the second should be the tickers. Alternatively, clusters is a list 
  of labels for the columns of dataframe.

  """
  df_c = copy.deepcopy(df)

  ticker_to_sector_dict = {ticker : ticker_to_sector_dict[ticker] for ticker in df_c.columns}

  if df_c.columns.nlevels == 1:
    df_c.columns = pd.MultiIndex.from_arrays((df_c.columns.map(ticker_to_sector_dict),
                                                    df_c.columns),
                                                    names=['Industry', 'Ticker'])

  for industry in set(ticker_to_sector_dict.values()):
    df_c[industry] = df_c[industry].sub(df_c[industry].mean(axis = 1), axis = 0)
  
  df_c.columns = df_c.columns.droplevel()
  
  return df_c

def ROR(df):  
  """
  Returns the percent change between time intervals of length 'period'. Period 
  is set to 1 by default.
  """

  df.dropna(axis = 1, inplace = True)

  ROR_df = df.pct_change().dropna()

  return ROR_df  

def default_transform_sequence(
        default_funcs = [ROR, market_adjust, industry_adjust], 
        default_additional_args = [{}, {}, {}]
        ) -> dict:
    """
    This function constructs the sequence of functions with their additional
    arguments (if any) to be used as the sequence of default transformations
    to be applied to a dataframe before it is fed to the `ClusterInput' object.
    
    The expected structure of the function is for it to have `df` as a primary
    argument, and possibly other additional arguments.
    
    Parameters
    ----------
    - default_funcs : List[Callable]
        The list of functions to be applied, in order. For e.g., if 
        default_funcs = [f1, f2, f3], the functions will be applied
        to the variable `var` as follows: f3(f2(f1(var))).
        (Ignoring additional arguments in this example.)

    - default_additional_args : List[Dict[str, Any]]
        The list of additional arguments as dictionaries. For e.g. if the functions
        are the following
        f1 = lambda x, y, z : x + y + z;
        f2 = lambda x, y : x - 2 * y;
        f3 = lambda x : x ** 2;
        then a possible default_additional_args would be:
        default_additional_args = [{'y' : 2, 'z' : 3}, {'y' : 1}, {}].
        
    Returns
    -------
    - transformation_sequence : List[Tuple[Callable, Dict[str, Any]]]
    A list of transformations to be applied in order, where any additional arguments
    besides the `df` argument are the default_additional_args arguments.
    """
    
    if any(list(signature(f).parameters.keys())[0] != 'df' for f in default_funcs):
       raise NameError("The first argument of every single default function should be `df`.")
    
    return [partial(f, **add_args) for (f, add_args) in zip(default_funcs, default_additional_args)]

def default_transform(df, transformation_sequence = default_transform_sequence()):
   """
   This represents the default transformation to be applied to our dataframe of
   adjusted closing prices before it is converted into a `ClusterInput` object.
   
   Parameter
   ---------
   - df : pd.DataFrame
      The dataframe of adjusted closing prices to be transformed.
   - transformation_sequence : List[Tuple(Callable, Dict[str, Any])]
        The transformation sequence to be applied.

   Returns
   -------
   - df_tr : pd.DataFrame
      The transformed dataframe to be converted into a `ClusterInput` object.
   """

   composite_transformation = lambda df : reduce(lambda res, f: f(res), transformation_sequence, df)

   df_tr = composite_transformation(df)
   
   return df_tr

class ClusterInput:
    def __init__(self, df : pd.DataFrame, 
                 transform : Callable[[pd.DataFrame], pd.DataFrame] = default_transform,
                 normalize = False, 
                 API = 'sklearn'):
        if df.index.name != 'Date' and df.index.inferred_type != 'datetime':
           raise ValueError("The index should be `Date` with `datetime` objects as its values.")
        
        self.df = df
        self.transform = transform
        self.normalize = normalize
        self.API = API
        
        if self.transform is None:
           self.transform = lambda df : df
        if normalize == True:
           self.transform = lambda df : normalize(self.transform(self.df))
        
        self.df = self.transform(self.df) if API is None else self.transform(self.df).T
