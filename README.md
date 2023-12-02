# Asset Selection & Diversification By Means Of Clustering

## Overview
Portfolio optimization is one of the central problems of modern finance where one aims to maximize the expected return of a portfolio
given a prescribed level of risk. This approach to investing relies on a careful and systematic selection of assets. Generally,
one seeks to have a diversified portfolio of assets to minimize losses due to unforeseen catastrophic events (e.g. the COVID-19 pandemic).

There is no standard method for portfolio diversification, and it is often very challenging to come up with non-naïve selection method.
In this project, we propose clustering algorithms as a systematic method of selecting assets for the purposes of portfolio construction.
More precisely, we seek to cluster the time series corresponding to these assets as our method of portfolio diversification. We will
specifically consider the S&P 500 as our universe of assets. The cluster-oriented approach is fairly natural in this context when we
note that numerous non-quantitative but popular selection methods, such as sector diversification, effectively group the portfolio
assets into clusters.

The assets that are selected as a result of our clustering can then be further used as the universe of assets serving as the basis
of a trading strategy or portfolio optimization framework. In general, the clustering can serve as a foundational layer
for numerous financial applications.  

### Stakeholders

- Financial Analysts and Portfolio Managers: Main users who could use
the clustering model for diversification, risk assessment, and
implementing statistical arbitrage strategies.
  
- FinTech Companies: Could integrate the clustering model into their
analytics tools.
  
- Regulatory Authorities: Might employ the model for market
surveillance and systemic risk assessment.

- Retail Investors: Could use this model as a means of robustifying their asset allocation.

### KPIs

- **Model Accuracy:** Effectiveness of the clusters will be assessed using
metrics like the Silhouette score and Davies–Bouldin index.
  
- **Computational Efficiency:** Time efficiency in model training and
application, targeting real-time or near-real-time use.
  
- **Return on Investment:** Evaluates the profitability of trading
strategies derived from the model. This will be particularly crucial
for stakeholders interested in statistical arbitrage opportunities. We
can also compare the return against baseline models and trading
strategies.

## Dataset Details
Our primary source of data consists of historical data from [Yahoo! Finance](https://finance.yahoo.com/) acquired using [`yfinance`](https://github.com/ranaroussi/yfinance). For each ticker (e.g. `APPL`), the data consists of the following daily (in the sense of trading days) information:
* Open -- the open price for the given stock in that day.
* High -- the highest price for the given stock in that day.
* Low -- the lowest price for the given stock in that day.
* Close -- the close price of the given stock in that day; adjusted for splits.
* Adj Close -- the close price, in that day, adjusted for splits and dividend and/or capital gain distributions.
* Volume -- the number of shares of the stock that were traded in that day.

See [this webpage](https://finance.yahoo.com/quote/AAPL/history?p=APPL) for an example of historical data for `APPL`.

Our data collection is explained in more detail in the Data Retrieval notebook.

## Modeling Approach

### Data Exploration

In order to choose a suitable clustering method, we need to understand what our data looks like (see [this webpage](https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html)).


### Data Processing

To make it easier to interpret our data, we made the following adjustments.

* Normalizations:
    * We initially normalized our data with respect to the $L^2$ norm.
    * We ultimately decided that rate of return (ROR) makes more sense, given the nature of our data.
* Market adjustment:
    * Market trends can make all stocks move together, artificially
    * increasing correlations between stocks. We subtract from each 
    * time series the mean value of the time series.
* Industry adjustment:
    * To remove the effect of industry, we remove the mean ROR for
    * each industry for each time series corresponding to a ticker in
    * that industry. This allows us to look for outliers within each
    * industry cluster.

These ideas are illustrated in the EDA notebook.

We concluded that k-means (or DBSCAN) would be appropriate methods for clustering our data.

### Benchmarks
* To judge the clusters we obtain via k-means, we compare them to the clustering of the SP500 by industry.
* We used the Calinski-Harabasz (See [this website](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.calinski_harabasz_score.html) for more details.) This can be found in the Kmeans notebook.
  

### Summary

![Summary](/Images/pipeline.png "Summary").


## Future Iterations & Extensions

The clusters we obtain can be used as the starting point of 
a trading strategy similar to 'pairs trading' 
(see [this paper](http://stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingQFin05.pdf) for more details).

In pairs trading, the idea is to find pairs of tickers that behave similarly.
When the prices of the tickers behave in opposite ways - i.e. one of the tickers goes up in value,
while the other goes down - we invest with the expectation that the trend will reverse itself.

* While traditional pairs trading restricts to clusters with only 2 elements, we can adapt the idea to work with clusters with more than 2 elements.
* We can try and optimize the trading strategy by applying a classification algorithm to historical data using days with high dispersion.

