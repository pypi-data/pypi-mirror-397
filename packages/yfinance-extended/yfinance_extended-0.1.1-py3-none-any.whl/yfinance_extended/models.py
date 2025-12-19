import datetime
from typing import List, Union
from pydantic import BaseModel, Field, field_validator
import yfinance as yf

class StockSymbols(BaseModel):
    """
    Model to unpack yfinance ticker/tickers or strings to a list for easier batch processing
    :param symbols: A list of symbols
    """
    symbols: List[str] = Field(description="List of symbols")

    def __init__(self, *args, **kwargs):
        # Extract the 'symbols' argument if passed as a positional argument
        if len(args) > 0:
            kwargs['symbols'] = args[0]
        super().__init__(**kwargs)

    @field_validator('symbols', mode='before')
    @classmethod
    def __parse_yf_ticker_to_str_list(cls, value: Union[yf.Ticker, yf.Tickers, str, List[str]]) -> List[str]:
        if isinstance(value, yf.Ticker):
            return [value.ticker]
        elif isinstance(value, yf.Tickers):
            return value.symbols
        elif isinstance(value, str):
            return [value.upper()]
        elif isinstance(value, list):
            # Ensure all elements in the list are strings
            return [str(item).upper() for item in value]
        else:
            raise TypeError("Invalid symbols type")
        
class LiveQuote(BaseModel):
    symbol: str
    bid: float
    ask: float
    bidSize: int
    askSize: int
    accessTime: datetime.datetime

class LiveOptionsQuote(BaseModel):
    symbol: str
    contractSymbol: str
    lastTradeDate: datetime.datetime
    strike: float
    lastPrice: float
    bid: float
    ask: float
    change: float
    percentChange: float
    volume: int
    openInterest: int
    impliedVolatility: float
    inTheMoney: bool
    contractSize: str
    currency: str
    accessTime: datetime.datetime