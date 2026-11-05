"""Web app. Runs the pipeline every hour and serves results.
Start: uvicorn app:app --reload"""
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
import scorer, db
from config import ASSETS, HORIZONS

app = FastAPI()
sched = BackgroundScheduler()

def job():
    scorer.resolve_old()
    scorer.run_all()

@app.on_event("startup")
def start():
    sched.add_job(job, "interval", hours=1, next_run_time=None)
    sched.start()
    if not db.latest_run()[1]:
        job()

@app.get("/api/latest")
def latest():
    ts, data = db.latest_run()
    return {"run_time": ts, "assets": data}

@app.get("/api/asset/{key}")
def asset(key: str):
    key = key.upper()
    if key not in ASSETS: return JSONResponse({"error": "unknown asset"}, 404)
    return scorer.score_asset(key)

@app.get("/api/accuracy")
def accuracy():
    return db.accuracy()

@app.post("/api/run")
def run_now():
    job(); return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html") as f: return f.read()
