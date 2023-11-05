import pandas as pd

def one_cluster(ticker_prices):
  """
  Baseline model: everything is in one cluster
  """
  tickers = ticker_prices.columns
  return {tick : 0 for tick in tickers}

def different_clusters(ticker_prices):
  """
  Baseline mode: everything in different clusters
  """
  tickers = ticker_prices.columns
  return {tick : i for (i, tick) in enumerate(tickers)}

def industry(ticker_prices):
  """
  Returns clustering based on industry. Uses code 
  from EDA notebook.

  """
  tickers = ticker_prices.columns

  industries = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
  industries = industries[0][["Symbol", "GICS Sector"]].set_index("Symbol")["GICS Sector"].to_dict()
  return {tick : industries[tick] for tick in tickers}
