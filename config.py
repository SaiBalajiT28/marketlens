"""Settings. Everything shown on the site is in Indian rupees."""

# Stocks scored every hour (NSE tickers, Yahoo format). Add or remove freely.
STOCKS = {
    "RELIANCE":  "Reliance Industries",
    "TCS":       "Tata Consultancy Services",
    "HDFCBANK":  "HDFC Bank",
    "INFY":      "Infosys",
    "ICICIBANK": "ICICI Bank",
    "SBIN":      "State Bank of India",
    "TATASTEEL": "Tata Steel",
    "ITC":       "ITC",
}
INDEX_TICKER = "^NSEI"      # Nifty 50, for market context

# Metals: international spot in USD per troy ounce, converted to INR
METALS = {
    "GOLD":   {"ticker": "GC=F", "name": "Gold",   "unit_grams": 10,   "purity": "24K"},
    "SILVER": {"ticker": "SI=F", "name": "Silver", "unit_grams": 1000, "purity": "999"},
}
USDINR_TICKER = "USDINR=X"
TROY_OUNCE_GRAMS = 31.1035
# India landed-price estimate on top of international spot. Check current rates and edit.
IMPORT_DUTY_PCT = 6.0
GST_PCT = 3.0

# Horizons predicted, in hours
HORIZONS = {"1h": 1, "6h": 6, "1d": 24, "1w": 24 * 7, "1m": 24 * 30}

GLOBAL_FEEDS = [
    "https://news.google.com/rss/search?q=stock+market+today&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=RBI+OR+Fed+interest+rates&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=crude+oil+OR+rupee+dollar&hl=en-IN&gl=IN&ceid=IN:en",
]
MAX_NEWS_PER_ASSET = 15
DB_PATH = "marketlens.db"
LLM_MODEL = "llama-3.3-70b-versatile"   # Groq model; see console.groq.com/docs/models
