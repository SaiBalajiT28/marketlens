"""Sentiment + fundamentals read.
Default: keyword scoring of headlines, no API needed.
If GROQ_API_KEY is set (free at console.groq.com, no card), an LLM reads the
headlines and writes a reason. Falls back to keywords on any error."""
import os, json, requests
from config import LLM_MODEL

POS = ["jump", "surge", "rally", "gain", "record", "beat", "upgrade", "buy", "profit", "growth",
       "strong", "soar", "high", "bullish", "rise", "up ", "boost", "outperform", "dividend"]
NEG = ["fall", "drop", "plunge", "slump", "loss", "miss", "downgrade", "sell", "weak", "cut",
       "bearish", "decline", "low", "crash", "fraud", "probe", "penalty", "default", "slide", "down "]

def _keyword(name, asset_news, global_news):
    score, hits = 0, []
    for n in asset_news:
        t = n["title"].lower()
        p = sum(w in t for w in POS); q = sum(w in t for w in NEG)
        if p > q: score += 1; hits.append("+ " + n["title"][:60])
        elif q > p: score -= 1; hits.append("- " + n["title"][:60])
    for n in global_news:  # macro counts half
        t = n["title"].lower()
        score += 0.5 * (sum(w in t for w in POS) > sum(w in t for w in NEG)) - 0.5 * (sum(w in t for w in NEG) > sum(w in t for w in POS))
    total = max(1, len(asset_news) + len(global_news) / 2)
    s = max(-2, min(2, 4 * score / total))
    return {"sentiment": round(s, 2), "confidence": 0.4 if asset_news else 0,
            "reason": f"{len(asset_news)} headlines scanned, {'leaning positive' if s > 0.3 else 'leaning negative' if s < -0.3 else 'mixed'}. " + (" · ".join(h[2:] for h in hits[:2]) if hits else ""),
            "fundamental_note": "none (keyword mode)"}

PROMPT = """You are a careful financial analyst. Asset: {name}.

Recent asset news headlines:
{asset_news}

Recent global/macro headlines:
{global_news}

Respond ONLY with JSON, no markdown:
{{"sentiment": <number from -2 (very bearish) to 2 (very bullish)>,
  "confidence": <0 to 1>,
  "reason": "<one or two plain sentences on why>",
  "fundamental_note": "<one sentence on fundamentals/valuation/earnings if the news mentions them, else 'none'>"}}"""

def analyze(name, asset_news, global_news):
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return _keyword(name, asset_news, global_news)
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": LLM_MODEL, "temperature": 0, "max_tokens": 400,
                  "messages": [{"role": "user", "content": PROMPT.format(
                      name=name,
                      asset_news="\n".join("- " + n["title"] for n in asset_news) or "(none)",
                      global_news="\n".join("- " + n["title"] for n in global_news) or "(none)")}]},
            timeout=60)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        return json.loads(text.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        r = _keyword(name, asset_news, global_news); r["reason"] += f" (LLM failed: {e})"; return r
