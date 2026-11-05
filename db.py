import sqlite3, json, time
from config import DB_PATH

def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY, ts REAL, asset TEXT, ticker TEXT, horizon TEXT,
        price REAL, prob_up REAL, label TEXT,
        resolved INTEGER DEFAULT 0, actual_price REAL, correct INTEGER)""")
    return c

def save_predictions(results):
    c, now = conn(), time.time()
    for key, r in results.items():
        for h, p in r["horizons"].items():
            c.execute("INSERT INTO predictions(ts,asset,ticker,horizon,price,prob_up,label) VALUES(?,?,?,?,?,?,?)",
                      (now, key, r["ticker"], h, r["price_raw"], p["prob_up"], p["label"]))
    c.commit(); c.close()

def unresolved():
    c = conn()
    rows = c.execute("SELECT id,ts,ticker,horizon,price,label FROM predictions WHERE resolved=0").fetchall()
    c.close(); return rows

def resolve(pid, actual, correct):
    c = conn()
    c.execute("UPDATE predictions SET resolved=1,actual_price=?,correct=? WHERE id=?", (actual, correct, pid))
    c.commit(); c.close()

def accuracy():
    c = conn()
    rows = c.execute("""SELECT asset,horizon,COUNT(*),SUM(correct) FROM predictions
        WHERE resolved=1 AND label!='no edge' GROUP BY asset,horizon ORDER BY asset""").fetchall()
    c.close()
    return [{"asset": a, "horizon": h, "n": n, "accuracy": round(s / n, 3) if n else None} for a, h, n, s in rows]
