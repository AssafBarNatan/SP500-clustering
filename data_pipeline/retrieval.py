"""Utilities to download data."""

import pandas as pd
import yfinance as yf
import logging
from datetime import datetime

WIKI_TABLE_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

TODAY = datetime.today()

class DataBank:
    def __init__(self, table_source = WIKI_TABLE_URL):
        self.table_source = table_source

    def get_table(self, html_source = None) -> pd.DataFrame:
        if html_source is None:
            html_source = WIKI_TABLE_URL
        return pd.read_html(html_source)[0]

    def get_tickers(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(table["Symbol"])

    def get_sectors_list(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(table["GICS Sector"].unique())

    def get_subind_list(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(list(table["GICS Sub-Industry"].unique()))

    def get_sector(self, ticker : str, table = None):
        if table is None:
            table = self.get_table()        
        return table[table.Symbol == ticker]["GICS Sector"].values[0]

    def get_subind(self, ticker : str, table = None):
        if table is None:
            table = self.get_table()        
        return table[table.Symbol == ticker]["GICS Sub-Industry"].values[0]

    def ticker_to_sector_map(self, table = None):
        if table is None:
            table = self.get_table()
        
        tickers = self.get_tickers(table)

        return {
            ticker : self.get_sector(ticker, table)
            for ticker in tickers
            }
    
    def ticker_to_subind_map(self, table = None):
        if table is None:
            table = self.get_table()
        
        tickers = DataBank.get_tickers(self, table)

        return {
            ticker : self.get_subind(ticker, table)
            for ticker in tickers
            }

    def sector_to_ticker_map(self, table = None):
        if table is None:
            table = self.get_table()
        
        tickers = DataBank.get_tickers(self, table)

        sectors = DataBank.get_sectors_list(self, table)

        return {
            sector : [ticker for ticker in tickers if self.get_sector(ticker, table) == sector]
            for sector in sectors
        }
    
    def subind_to_ticker_map(self, table = None):
        if table is None:
            table = self.get_table()
        
        tickers = DataBank.get_tickers(self, table)

        subinds = DataBank.get_sectors_list(self, table)

        return {
            subind : [ticker for ticker in tickers if self.get_subind(ticker, table) == subind]
            for subind in subinds
        }

def download_historical_data(tickers : str, start : str, end = TODAY, save_data : bool = True) -> pd.DataFrame:
    start = datetime.fromisoformat(start)
    
    end = datetime.fromisoformat(end) if not end else end

    start = start.strftime('%Y-%m-%d')
    end = end if type(end) == str else end.strftime('%Y-%m-%d')
    data_path = f"./data/dataframes/historical_data/SP500_{start}_{end}.pkl"

    try:
        historical_data = pd.read_pickle(data_path)
        print("Loaded data from saved file")
        return historical_data
    except Exception as e:
        print("Failed to load saved data. Loading data...")

    historical_data = yf.download(
        tickers,
        start,
        end
    )
    historical_data.dropna(axis=1, inplace=True)

    if save_data:
        historical_data.to_pickle(data_path)
    return historical_data

def download_adj_close(tickers : str, start : str, end = TODAY, save_data : bool = True) -> pd.DataFrame:
    """
    Parameter
    ---------
    - tickers: str
        The tickers under consideration.
    - start: str
        The start date in 'YYYY-MM-DD' format.
    - end: str
        The end date in 'YYYY-MM-DD' format. (Today's date as a `datetime` object by default.)
    - save_data: bool
        A boolean indicating whether or not the data is to be saved (as a pickle file).

    Returns
    -------
        A dataframe containing the adjusted closing prices.
    """
    start = start
    end = end if type(end) == str else end.strftime('%Y-%m-%d')
    data_path = f"./data/dataframes/closing_prices/SP500_{start}_{end}.pkl"

    try:
        adj_closing_prices = pd.read_pickle(data_path)
        print("Loaded from saved data!")
        return adj_closing_prices
    except Exception as e:
        print("Data for this time interval not found. Loading data...")
        adj_closing_prices = download_historical_data(tickers, start, end, save_data=False)['Adj Close']

    if save_data:
        adj_closing_prices.to_pickle(data_path)
    
    return adj_closing_prices

def load(load_path : str) -> pd.DataFrame:
    """
    Parameter
    ---------
    - load_path: str
        The path from which the data will be loaded. (Assumed to be a pickle file.)
    
    Returns
    -------
        A data frame of the data extracted from the pickle file.
        If the file does not exist, an error will be raised instead.
    """
    try:
        data = pd.read_pickle(load_path)
    except FileNotFoundError:
        logging.exception("The specified file does not exist. Please double check the loading path.")
    
    return data
