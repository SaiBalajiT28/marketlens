"""Scores one asset (stock or metal) and runs the hourly batch."""
import time, json, os, sys, traceback
from config import STOCKS, METALS, HORIZONS, INDEX_TICKER
import prices, technical, news, sentiment, model, metals, db

def _label(p):
    if p >= 0.6: return "lean buy"
    if p <= 0.4: return "lean sell"
    return "no edge"

def _horizons(hdf, ddf, s, tech_score):
    out = {}
    for h, hrs in HORIZONS.items():
        use_hourly = hrs <= 24
        q, bt = model.prob_up(hdf if use_hourly else ddf, hrs, hourly=use_hourly)
        w_sent = 0.08 if hrs <= 24 else 0.04
        p = min(0.95, max(0.05, q + w_sent * s + 0.05 * tech_score))
        out[h] = {"prob_up": round(p, 3), "label": _label(p), "quant_backtest_acc": round(bt, 3)}
    return out

def _common(ticker, name, news_terms, gnews):
    hdf, ddf = prices.hourly(ticker), prices.daily(ticker)
    tf = technical.features(hdf)
    tech_score, tech_note = technical.summary(tf)
    anews = news.search(news_terms)
    sent = sentiment.analyze(name, anews, gnews)
    s = float(sent.get("sentiment", 0)) * float(sent.get("confidence", 0))
    close = hdf["Close"]
    return {
        "ticker": ticker, "name": name, "price_raw": float(close.iloc[-1]),
        "change_1d_pct": round(float(close.iloc[-1] / ddf["Close"].iloc[-2] - 1) * 100, 2) if len(ddf) > 1 else None,
        "change_1w_pct": round(float(close.iloc[-1] / ddf["Close"].iloc[-6] - 1) * 100, 2) if len(ddf) > 6 else None,
        "horizons": _horizons(hdf, ddf, s, tech_score),
        "reasons": {"technical": tech_note, "sentiment": sent.get("reason"),
                    "fundamental": sent.get("fundamental_note"), "sentiment_score": round(s, 2),
                    "rsi": round(float(tf["rsi"].iloc[-1]), 1)},
        "news": anews[:5], "scored_at": time.time(),
    }

def score_stock(symbol, gnews=None, name=None):
    symbol = symbol.upper().replace(".NS", "")
    ticker = symbol + ".NS"
    name = name or STOCKS.get(symbol) or prices.name_of(ticker)
    r = _common(ticker, name, f"{name} share", gnews or news.global_news())
    r.update({"kind": "stock", "symbol": symbol, "price_inr": round(r["price_raw"], 2)})
    return r

def score_metal(key, usdinr, gnews=None):
    m = METALS[key]
    r = _common(m["ticker"], m["name"], f"{m['name'].lower()} price India", gnews or news.global_news())
    r.update({"kind": "metal", "symbol": key, "rates": metals.describe(key, r["price_raw"], usdinr)})
    return r

def resolve_old():
    now = time.time()
    for pid, ts, ticker, horizon, price, label in db.unresolved():
        if now - ts < HORIZONS[horizon] * 3600: continue
        try: actual = prices.last_price(ticker)
        except Exception: continue
        up = actual > price
        correct = int((label == "lean buy" and up) or (label == "lean sell" and not up))
        db.resolve(pid, actual, correct)

def run_hourly():
    resolve_old()
    gnews = news.global_news()
    results, errors = {}, {}
    try: usdinr = prices.usdinr()
    except Exception as e: usdinr = None; errors["USDINR"] = str(e)
    for key in METALS:
        try: results[key] = score_metal(key, usdinr, gnews); print("[ok]", key)
        except Exception as e: errors[key] = str(e); traceback.print_exc()
    for sym, nm in STOCKS.items():
        try: results[sym] = score_stock(sym, gnews, nm); print("[ok]", sym)
        except Exception as e: errors[sym] = str(e); traceback.print_exc()
    try:
        idx = prices.daily(INDEX_TICKER)["Close"]
        nifty = {"level": round(float(idx.iloc[-1]), 2), "change_1d_pct": round(float(idx.iloc[-1] / idx.iloc[-2] - 1) * 100, 2)}
    except Exception as e:
        nifty = None; errors["NIFTY"] = str(e)
    db.save_predictions(results)
    os.makedirs("docs", exist_ok=True)
    json.dump({"run_time": time.time(), "usdinr": usdinr, "nifty": nifty, "assets": results, "errors": errors},
              open("docs/latest.json", "w"))
    json.dump(db.accuracy(), open("docs/accuracy.json", "w"))
    try:
        import ogimage; ogimage.make(); ogimage.stamp_html()
    except Exception as e:
        print("[warn] preview image failed:", e)
    return results

if __name__ == "__main__":
    run_hourly()
