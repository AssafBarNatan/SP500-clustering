"""Utilities to download data."""

import pandas as pd
import yfinance as yf
import logging
from datetime import datetime

WIKI_TABLE_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

TODAY = datetime.today()

class DataBank:
    def __init__(self, 
                 table_source = WIKI_TABLE_URL, 
                 table_num = 0, 
                 ticker_col_name = 'Symbol', 
                 sector_col_name = 'GICS Sector',
                 subind_col_name = 'GICS Sub-Industry'):
        self.table_source = table_source
        self.table_num = table_num
        self.ticker_col_name = ticker_col_name
        self.sector_col_name = sector_col_name
        self.subind_col_name = subind_col_name

    def get_table(self, html_source = None) -> pd.DataFrame:
        if html_source is None:
            html_source = WIKI_TABLE_URL
        return pd.read_html(html_source)[self.table_num]

    def get_tickers(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(table[self.ticker_col_name])

    def get_sectors_list(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(table[self.sector_col_name].unique())

    def get_subind_list(self, table = None) -> list[str]:
        if table is None:
            table = self.get_table()
        return list(list(table[self.subind_col_name].unique()))

    def get_sector(self, ticker : str, table = None):
        if table is None:
            table = self.get_table()        
        return table[table.Symbol == ticker][self.sector_col_name].values[0]

    def get_subind(self, ticker : str, table = None):
        if table is None:
            table = self.get_table()        
        return table[table.Symbol == ticker][self.subind_col_name].values[0]

    def ticker_to_sector_map(self, table = None, tickers = None):
        if table is None:
            table = self.get_table()
        
        if tickers is None:
            tickers = self.get_tickers(table)

        return {
            ticker : self.get_sector(ticker, table)
            for ticker in tickers
            }
    
    def ticker_to_subind_map(self, table = None, tickers = None):
        if table is None:
            table = self.get_table()
        
        if tickers is None:
            tickers = self.get_tickers(table)

        return {
            ticker : self.get_subind(ticker, table)
            for ticker in tickers
            }

    def sector_to_ticker_map(self, table = None, tickers = None):
        if table is None:
            table = self.get_table()
        
        if tickers is None:
            tickers = self.get_tickers(table)

        tick_to_sec_map = self.ticker_to_sector_map(table, tickers)

        sectors = set(tick_to_sec_map.values())

        sec_to_tick_map = {sector : [] for sector in sectors}

        for ticker in tick_to_sec_map.keys():
            for sector in sectors:
                if tick_to_sec_map[ticker] == sector:
                    sec_to_tick_map[sector].append(ticker)

        return sec_to_tick_map 
    
    def subind_to_ticker_map(self, table = None):
        if table is None:
            table = self.get_table()
        
        if tickers is None:
            tickers = self.get_tickers(table)

        tick_to_sub_map = self.ticker_to_sector_map(table, tickers)

        subinds = set(tick_to_sub_map.values())

        sub_to_tick_map = {subind : [] for subind in subinds}

        for ticker in tick_to_sub_map.keys():
            for subind in subinds:
                if tick_to_sub_map[ticker] == subind:
                    sub_to_tick_map[subind].append(ticker)

def download_historical_data(tickers : list[str], start : str, end = TODAY, save_data : bool = True) -> pd.DataFrame:
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

def download_adj_close(tickers : list[str], start : str, end = TODAY, save_data : bool = True) -> pd.DataFrame:
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
