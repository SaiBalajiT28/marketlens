import feedparser, urllib.parse
from datetime import datetime, timezone, timedelta
from config import GLOBAL_FEEDS, MAX_NEWS_PER_ASSET

def _parse(url, hours=48):
    out, cutoff = [], datetime.now(timezone.utc) - timedelta(hours=hours)
    for e in feedparser.parse(url).entries:
        try: pub = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
        except Exception: pub = datetime.now(timezone.utc)
        if pub < cutoff: continue
        out.append({"title": e.title, "published": pub.isoformat(), "link": e.get("link", "")})
    return out

def search(terms):
    q = urllib.parse.quote(terms)
    return _parse(f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en")[:MAX_NEWS_PER_ASSET]

def global_news():
    items = []
    for u in GLOBAL_FEEDS: items += _parse(u, hours=24)[:10]
    return items
