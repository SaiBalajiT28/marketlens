"""Quant layer: logistic regression trained on this asset's own history.
Target = did price go up after N bars? One model per asset per horizon."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from technical import features

def _bars(horizon_hours, df_is_hourly):
    return horizon_hours if df_is_hourly else max(1, round(horizon_hours / 24))

def prob_up(df, horizon_hours, hourly=True):
    f = features(df)
    n = _bars(horizon_hours, hourly)
    y = (df["Close"].shift(-n) > df["Close"]).astype(int)
    data = f.join(y.rename("y")).dropna()
    if len(data) < 60:
        return 0.5, 0.5
    X, Y = data.drop(columns="y").values, data["y"].values
    if Y.min() == Y.max():
        return 0.5, 0.5
    split = int(len(X) * 0.8)
    m = LogisticRegression(max_iter=500).fit(X[:split], Y[:split])
    test_acc = float((m.predict(X[split:]) == Y[split:]).mean()) if split < len(X) else 0.5
    p = float(m.predict_proba(f.dropna().iloc[[-1]].values)[0, 1])
    return p, test_acc
