from typing import Optional
import datetime
import pytz
import pandas as pd

def rename_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    The returned index is named "Datetime" when period is shorter than 1d, but "Date" when longer
    We'll format it to "Datetime"
    :return: Pandas dataframe
    """
    if df.index.name == "Date":
        df.index.rename("Datetime", inplace=True)
    return df


def flatten_by_symbol(df: pd.DataFrame, symbol_for_single_symbol_df: Optional[str]=None) -> pd.DataFrame:
    """
    The downloaded data is in a dataframe with two levels of column labels
    One level is the tickers, and the other is Open, Close, etc.
    We'll flatten it by adding a Symbol Column, and remove the index
    :param df: Price dataframe downloaded from yfinance, with two levels of columns
    :param symbol_for_single_symbol_df: Symbol for single symbol df
    :return: Pandas dataframe without index
    """
    # Pivot only if the number of column levels is greater than one (passing one symbol gives only one level)
    if df.columns.nlevels > 1:
        df = df.rename_axis(columns=('Symbol', None)).stack(0, future_stack=True).reset_index().explode('Datetime')
    else:
        df = df.reset_index()
        if symbol_for_single_symbol_df == None:
            raise TypeError("Dataframe contains one symbol, but missing symbol_for_single_symbol_df in argument")
        df.insert(loc=1, column="Symbol", value=symbol_for_single_symbol_df)
    return df


def __get_exchange_tz(timezone: str) -> datetime.tzinfo:
    """
    Get timezone given exchange's country
    :param market: Country of the Exchange
    :return:
    """

    if timezone != "UTC":
        return pytz.timezone(timezone)
    else:
        return pytz.timezone("UTC")


def __df_to_exchange_tz(df: pd.DataFrame, exchangeTimeZoneName: str) -> pd.DataFrame:
    # Get Exchange timezone
    exchange_tz = __get_exchange_tz(exchangeTimeZoneName)

    # If dataframe is timezone naive
    if df["Datetime"].dt.tz is None:
        df["Datetime"] = df["Datetime"].dt.tz_localize(exchange_tz)

    # If dataframe is timezone aware
    elif df["Datetime"].dt.tz != __get_exchange_tz(exchangeTimeZoneName):
        df["Datetime"] = df["Datetime"].dt.tz_convert(exchange_tz)

    return df


def add_market_open_close_col(df: pd.DataFrame, exchangeTimeZoneName: str) -> pd.DataFrame:
    if exchangeTimeZoneName == "America/New_York":
        # Change dataframe's timezone to market's
        df = __df_to_exchange_tz(df, exchangeTimeZoneName)
        df["Market"] = df["Datetime"].apply(lambda x: "Closed" if x.time() < datetime.time(hour=9, minute=30) or
                                                                  x.time() > datetime.time(hour=16) else "Open")
    else:
        print("Market open/close status not supported yet.")
        df["Market"] = None
        return df
    return df