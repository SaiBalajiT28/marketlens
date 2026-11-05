# MarketLens

Hourly research signals for gold, silver and Indian stocks, in rupees. Every hour on the hour it gives the chance that the price is higher after 1h / 6h / 1d / 1w / 1m, with the reason, and logs each call so real accuracy is measured over time.

It is a research tool. Expect 50–60% on short horizons. Do not trade real money on it.

Live page: `https://<your-username>.github.io/marketlens/`

## What the page shows
- Gold 24K (and 22K, 18K) per 10 g; silver 999 per kg. International rate in ₹, plus an India estimate with import duty and GST added (edit `IMPORT_DUTY_PCT` and `GST_PCT` in `config.py`).
- NSE stocks in ₹ with hourly, daily, weekly and monthly signals, RSI, trend, volatility and volume.
- An on-demand check for any NSE symbol or GOLD / SILVER.
- A running accuracy table.

## Set up (free, no server)
1. Create a **public** repo and upload all files, including `.github` and `docs`.
2. Settings → Actions → General → Workflow permissions → **Read and write** → Save.
3. Settings → Pages → Deploy from a branch → `main`, folder `/docs` → Save.
4. Actions → hourly-scoring → Run workflow → wait for the green tick.
5. Open your page.

Optional, still free: a Groq API key (console.groq.com, no card) gives better news reading. Add it under Settings → Secrets and variables → Actions as `GROQ_API_KEY`. Without it, headlines are scored by keywords.

## Check one stock now
Actions → check-asset → Run workflow → type the NSE symbol (e.g. `TATASTEEL`) or `GOLD` / `SILVER` → Run. About two minutes later the result is on the page under "Check a particular stock or metal". The page's search box opens this workflow for you.

## Change the tracked list
Edit `STOCKS` in `config.py`. Any NSE symbol works with `.NS`.

## How it works
| Layer | File | What it does |
|---|---|---|
| Prices | prices.py | yfinance hourly (60d) and daily (3y) data, USD/INR rate |
| Metals in INR | metals.py | USD/oz → ₹ per 10 g (24K/22K/18K) and per kg; India duty + GST estimate |
| Technical | technical.py | RSI, moving-average gaps, volume, returns, volatility |
| News | news.py | Google News RSS per asset + global macro feeds |
| Sentiment | sentiment.py | Groq LLM if key present, else keyword scan |
| Quant | model.py | Logistic regression per asset per horizon on its own history |
| Combine | scorer.py / ondemand.py | hourly batch and single-asset check |
| Tracking | db.py | SQLite; resolves old predictions and reports accuracy |
| Page | docs/index.html | Static page reading docs/*.json |

Labels: ≥ 60% = buy, ≤ 40% = sell, else no edge.

## Known weaknesses
- `quant_backtest_acc` is on overlapping samples and is optimistic. Only trust the live accuracy table.
- Gold/silver are international spot via Yahoo, not MCX. The India rate is an estimate; jeweller prices also add making charges.
- Google News RSS is delayed. No real-time edge is possible with free feeds.
