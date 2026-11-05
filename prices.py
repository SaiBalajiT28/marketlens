import yfinance as yf
import pandas as pd

def _flat(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    if df.empty: raise ValueError("no price data from Yahoo (check the symbol; it may have changed)")
    return df

def hourly(ticker, days=60):
    return _flat(yf.download(ticker, period=f"{days}d", interval="1h", progress=False, auto_adjust=True))

def daily(ticker, years=3):
    return _flat(yf.download(ticker, period=f"{years}y", interval="1d", progress=False, auto_adjust=True))

def last_price(ticker):
    return float(hourly(ticker, days=5)["Close"].iloc[-1])

def usdinr():
    return last_price("USDINR=X")

def name_of(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("longName") or info.get("shortName") or ticker
    except Exception:
        return ticker
