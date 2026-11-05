"""Score one asset on request. Usage: python ondemand.py RELIANCE   (or GOLD / SILVER)"""
import sys, json, os, time
import scorer, prices, db
from config import METALS

def run(symbol):
    symbol = symbol.strip().upper().replace(".NS", "")
    if symbol in METALS:
        r = scorer.score_metal(symbol, prices.usdinr())
    else:
        r = scorer.score_stock(symbol)
    db.save_predictions({symbol: r})
    os.makedirs("docs/ondemand", exist_ok=True)
    json.dump(r, open(f"docs/ondemand/{symbol}.json", "w"))
    idx_path = "docs/ondemand/index.json"
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else []
    idx = [i for i in idx if i["symbol"] != symbol]
    idx.insert(0, {"symbol": symbol, "name": r["name"], "scored_at": r["scored_at"]})
    json.dump(idx[:50], open(idx_path, "w"))
    json.dump(db.accuracy(), open("docs/accuracy.json", "w"))
    print("[ok]", symbol, r["name"])

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit("give a symbol, e.g. python ondemand.py RELIANCE")
    run(sys.argv[1])
