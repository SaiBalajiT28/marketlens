"""Simple technical indicators. Returns a dict of features and a plain-English summary."""
import pandas as pd

def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = -d.clip(upper=0).rolling(n).mean()
    return 100 - 100 / (1 + up / dn.replace(0, 1e-9))

def features(df):
    c = df["Close"]
    f = pd.DataFrame(index=df.index)
    f["ret_1"] = c.pct_change()
    f["ret_5"] = c.pct_change(5)
    f["ret_20"] = c.pct_change(20)
    f["rsi"] = rsi(c)
    f["sma20_gap"] = c / c.rolling(20).mean() - 1
    f["sma50_gap"] = c / c.rolling(50).mean() - 1
    f["vol_20"] = f["ret_1"].rolling(20).std()
    if "Volume" in df and df["Volume"].sum() > 0:
        f["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
    else:
        f["vol_ratio"] = 1.0
    return f

def summary(f):
    last = f.iloc[-1]
    notes, score = [], 0.0
    if last["rsi"] > 70: notes.append(f"RSI {last['rsi']:.0f} overbought"); score -= 0.5
    elif last["rsi"] < 30: notes.append(f"RSI {last['rsi']:.0f} oversold"); score += 0.5
    else: notes.append(f"RSI {last['rsi']:.0f} neutral")
    if last["sma20_gap"] > 0 and last["sma50_gap"] > 0: notes.append("above 20 & 50 avg (uptrend)"); score += 0.5
    elif last["sma20_gap"] < 0 and last["sma50_gap"] < 0: notes.append("below 20 & 50 avg (downtrend)"); score -= 0.5
    if last["vol_ratio"] > 1.5: notes.append("volume above normal")
    return score, "; ".join(notes)
