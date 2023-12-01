import pandas as pd
import numpy as np

WIKI_TABLE_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

class SectorCluster:
    def __init__(self, 
                 table_source : str = WIKI_TABLE_URL, 
                 table_num : int = 0, 
                 ticker_col_name : str = 'Symbol', 
                 sector_col_name : str = 'GICS Sector'
                 ):
        self.table_source = table_source
        self.table_num = table_num
        self.ticker_col_name = ticker_col_name
        self.sector_col_name = sector_col_name

    def ticker_to_sector_map(self, tickers):
        if not (isinstance(tickers, list) and all([isinstance(ticker, str) for ticker in tickers])):
            raise ValueError("The input must be a list of tickers.")        
        
        table = pd.read_html(self.table_source)[self.table_num]

        return table[table[self.ticker_col_name].isin(tickers)][
            [self.ticker_col_name, self.sector_col_name]
            ].set_index(self.ticker_col_name).to_dict()[self.sector_col_name]
    
    def fit(self, df):
        tickers = list(df.columns)

        self.labels_ = np.array(
            list(self.ticker_to_sector_map(tickers).values())
        )
    
        return self

class SubindustryCluster:
    def __init__(self, 
                 table_source : str = WIKI_TABLE_URL, 
                 table_num : int = 0, 
                 ticker_col_name : str = 'Symbol', 
                 subind_col_name : str = 'GICS Sector'
                 ):
        self.table_source = table_source
        self.table_num = table_num
        self.ticker_col_name = ticker_col_name
        self.subind_col_name = subind_col_name

    def ticker_to_subind_map(self, tickers):
        if not (isinstance(tickers, list) and all([isinstance(ticker, str) for ticker in tickers])):
            raise ValueError("The input must be a list of tickers.")        
        
        table = pd.read_html(self.table_source)[self.table_num]

        return table[table[self.ticker_col_name].isin(tickers)][
            [self.ticker_col_name, self.subind_col_name]
            ].set_index(self.ticker_col_name).to_dict()[self.subind_col_name]
    
    def fit(self, df):
        tickers = df.columns
        
        self.labels_ = np.array(
            list(self.ticker_to_subind_map(tickers).values())
        )
    
        return self

