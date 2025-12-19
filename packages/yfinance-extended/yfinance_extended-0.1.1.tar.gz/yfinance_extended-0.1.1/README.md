# yfinance Package with Wide-Form Data Support and Data Export

**Note: currently being refactored to use Spark DataFrame instead of pandas to perform transformations.**

`yfinance-extended` extends `yfinance` package by Ran Aroussi and make it easier to:

1. Retrieve multiple-ticker intraday price data in a wide-form `pandas` dataframe;
2. Read options data for all available expiration dates;
3. Retrieve top-of-the-book bid-ask prices and size

## Sample Usage

### Get Historical Data

Getting past five days of minute-by-minute prices of Apple, Inc., including pre-/post-market data.

```python
import yfinance_extended as yfe

aapl = yfe.StockSymbols(symbols="AAPL")
aapl_price_df = get_historical_prices(aapl, period="5d", interval="1m", prepost=True)

symbols = yfe.StockSymbols(symbols=["AAPL", "GOOGL"])
prices_df = get_historical_prices(symbols, period="5d", interval="1m", prepost=True)
```

### Read all Available Options Information

```python
aapl = yfe.StockSymbols(symbols="AAPL")
options_df = yfe.get_live_options(aapl)
```

### Get Top-of-the-Book Data

```python
aapl = yfe.StockSymbols(symbols="AAPL")
aapl_price_df = yfe.get_live_quote(aapl)
live_prices_df = loader.get_prices(["AAPL", "GOOGL"])
```

Alternatively, if you wish to save all data into one file:

```python
# Write to one file
yfe.to_parquet(prices_df, filepath="./data/datafile.parquet")

# Read from the file
prices_df = yfe.read_parquet(filepath="./data/datafile.parquet")
```
