import pytz
import yfinance as yf
import datetime
from typing import Any, Dict, List
import pandas as pd
from .models import LiveOptionsQuote, LiveQuote, StockSymbols
from . import utils

def get_historical_quote(stockSymbols: StockSymbols,
                   start: Any = None,
                   end: Any = None,
                   period: str = "5d",
                   interval: str = "1m",
                   prepost: bool = True,
                   keepna: bool = False) -> pd.DataFrame:
        """
         Method to load previous trading session's data
         (Should run after 8pm Eastern Time / end of post-market session)

         Note: start/end parameters are broken for the moment
        :param start: Start date for historical data query
        :param end: End date for historical data query
        :param period: Period of query, default to 5 days (can be set to max in conjunction with start/end)
        :param interval: Resolution interval for data, smallest is 1 minute, but can only get the last 7 days
        :param prepost: Pre-/Post-market data
        :param keepna: Keep NA entries
        :return: A pandas dataframe of prices
        """
        tkrs = stockSymbols.symbols

        # Download ticker data from yahoo
        df = yf.download(tickers=tkrs,
                         start=start,
                         end=end,
                         period=period,
                         interval=interval,
                         prepost=prepost,
                         actions=True,
                         progress=False,
                         group_by="ticker",
                         threads=True,
                         keepna=keepna)

        df = utils.yf_price_df.rename_datetime_column(df)
        df = utils.yf_price_df.flatten_by_symbol(df, tkrs[0]) # Use first symbol as default symbol, if only one ticker is present the list
        df = utils.yf_price_df.add_market_open_close_col(df, exchangeTimeZoneName="America/New_York")
        return df

def get_live_quote(stockSymbols: StockSymbols) -> pd.DataFrame:
    """
    Given a StockSymbols, return last quote
    :param stockSymbols: StockSymbols
    :return: Regular market price, post market bid price, ask price, bid size, ask size, quote access datetime
    """

    symbols = stockSymbols.symbols
    symbols_df = pd.DataFrame(columns=LiveQuote.model_fields)

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        try:
            quote: LiveQuote = LiveQuote(
                 symbol=symbol,
                 bid=info["bid"],
                 ask=info["ask"],
                 bidSize=info["bidSize"],
                 askSize=info["askSize"],
                 accessTime=datetime.datetime.now(tz=datetime.timezone.utc)
            )
            symbol_df = pd.DataFrame([quote.model_dump()])
            symbols_df = pd.concat([symbols_df, symbol_df])
        except KeyError:
            pass # Add logging etc
    return symbols_df

def get_institutional_holdings() -> pd.DataFrame:
     pass

def get_live_options(symbols: StockSymbols) -> pd.DataFrame:

        tkrs = symbols.symbols
        options_df = pd.DataFrame()  # create an empty DataFrame to store options data

        for ticker in tkrs:

            ticker_options_df = pd.DataFrame(columns=LiveOptionsQuote.model_fields)
            # Get a list of expiration dates
            expiration_dates = yf.Ticker(ticker).options

            # yfinance does not provide a way to get all expiration date options price, so we have to query one by one
            for expiration_date in expiration_dates:
                option_chain = yf.Ticker(ticker).option_chain(
                    date=expiration_date)  # get the option chain for the ticker
                call_options = option_chain.calls  # get call options data
                put_options = option_chain.puts  # get put options data
                ticker_options_df = pd.concat(
                    [ticker_options_df, call_options, put_options])  # concatenate call and put options data
                ticker_options_df["accessTime"] = datetime.datetime.now(tz=pytz.UTC)
                ticker_options_df["symbol"] = ticker
            options_df = pd.concat([options_df, ticker_options_df])
        return options_df