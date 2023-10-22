"""Utilities to download data."""
import pandas as pd
import yfinance as yf
import logging
from datetime import datetime

def data_download(html_source : str, period : str = '3y', save_data : bool = True) -> pd.DataFrame:
    """
    Parameter
    ---------
    - html_source: str
        The HTML source of the data.
    - period: str
        The period. ('3y' by default.)
    - save_data: bool
        A boolean indicating whether or not the data is to be saved (as a pickle file).

    Returns
    -------
        A dataframe containing the closing prices.
    """
    # Fetch the list of S&P 500 tickers from Wikipedia
    df = pd.read_html(html_source)[0]
    tickers = df['Symbol'].tolist()
    
    equities = []

    for ticker in tickers:
        try:
            stock_data = yf.download(ticker, period = '3y')['Adj Close']
            stock_data.name = ticker  # Rename the Series to match the ticker
            equities.append(stock_data)
        except Exception as e:
            logging.exception(f"Failed to download data for {ticker}: {e}.")

    # Concatenate all the individual DataFrames
    closing_prices = pd.concat(equities, axis=1)
    closing_prices.dropna(axis=1, inplace=True)

    return closing_prices

    if sava_data:
        today_str = datetime.today().strftime('%Y-%m-%d')
        output_path = f"./closing_prices_SP500_{today_str}.pkl"
        closing_prices.to_pickle(output_path)

def load_data(load_path : str) -> pd.DataFrame:
    """
    Parameter
    ---------
    - load_path: str
        The path from which the data will be loaded. (Assumed to be a pickle file.)
    
    Returns
    -------
        A data frame of the closing prices extracted from the pickle file.
        If the file does not exist, an error will be raised instead.
    """
    try:
        closing_prices = pd.read_pickle(load_path)
    except FileNotFoundError:
        logging.exception("The specified file does not exist. Please double check the loading path.")
    
    return closing_prices
