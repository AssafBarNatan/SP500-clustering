"""Utilities to process the loaded data."""

import pandas as pd
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



