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

    def fit(self, tickers):
        table = pd.read_html(self.table_source)[self.table_num]

        ticker_to_sector_map = table[
            table['Symbol'].isin(tickers)
            ][
                [self.ticker_col_name, self.sector_col_name]
                ].set_index(self.ticker_col_name).to_dict()[self.sector_col_name]
        
        self.labels_ = np.array(
            list(ticker_to_sector_map.values())
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

    def fit(self, tickers):
        table = pd.read_html(self.table_source)[self.table_num]

        ticker_to_subind_map = table[
            table['Symbol'].isin(tickers)
            ][
                [self.ticker_col_name, self.subind_col_name]
                ].set_index(self.ticker_col_name).to_dict()[self.subind_col_name]
        
        self.labels_ = np.array(
            list(ticker_to_subind_map.values())
        )
    
        return self

