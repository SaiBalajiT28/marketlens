"""Gold and silver rates in INR, Indian units (gold per 10 g, silver per kg)."""
from config import METALS, TROY_OUNCE_GRAMS, IMPORT_DUTY_PCT, GST_PCT

def inr_rates(usd_per_oz, usdinr, grams):
    intl = usd_per_oz * usdinr / TROY_OUNCE_GRAMS * grams
    landed = intl * (1 + IMPORT_DUTY_PCT / 100) * (1 + GST_PCT / 100)
    return intl, landed

def describe(key, usd_per_oz, usdinr):
    m = METALS[key]
    intl, landed = inr_rates(usd_per_oz, usdinr, m["unit_grams"])
    out = {
        "unit": f"{m['unit_grams']} g" if m["unit_grams"] < 1000 else "1 kg",
        "purity": m["purity"],
        "usd_per_oz": round(usd_per_oz, 2),
        "usdinr": round(usdinr, 2),
        "inr_intl": round(intl),
        "inr_india_est": round(landed),
    }
    if key == "GOLD":
        out["inr_22k_est"] = round(landed * 22 / 24)
        out["inr_18k_est"] = round(landed * 18 / 24)
    return out
