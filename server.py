"""Server for the phone app: serves the app itself (static/) and the ML API.

Run locally:  .venv/bin/uvicorn server:app --port 8080   then open http://127.0.0.1:8080
On Cloud Run the Dockerfile starts this same command.
"""
import io
import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from hydrangea import pruning, weather
from hydrangea.config import TASKS
from hydrangea.predict import analyse

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
log = logging.getLogger("uvicorn.error")
app = FastAPI(title="Hydrangea Doctor", docs_url=None, redoc_url=None)


@app.get("/api/health")
def healthcheck():
    return {"ok": True}


@app.post("/api/analyze")
async def analyze(
    photo: UploadFile = File(...),
    species: str = Form("unknown"),
    age_years: float | None = Form(None),
    height_cm: float | None = Form(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
):
    if species not in pruning.SPECIES:
        raise HTTPException(400, "Unknown hydrangea type")
    data = await photo.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Photo is too large")
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "That file isn't a photo I can read")

    w, weather_note = None, None
    if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
        try:
            w = weather.fetch_coords(lat, lon)
        except Exception as e:  # weather is a bonus; never fail the whole request on it
            log.warning("weather failed: %s", e)
            weather_note = "Couldn't get the weather right now; advice ignores it."

    r = analyse(image, species, height_cm=height_cm or None, age_years=age_years or None, weather=w)
    adv = r["advice"]
    return {
        "trim_now": adv.trim_now,
        "headline": adv.headline,
        "how_far": adv.how_far,
        "notes": adv.notes,
        "weather": w.summary() if w else weather_note,
        **{task: {"label": r[task].label, "confidence": r[task].confidence,
                  "unsure": r[task].unsure, "method": r[task].method} for task in TASKS},
    }


@app.get("/api/species")
def species():
    return pruning.SPECIES


app.mount("/", StaticFiles(directory="static", html=True), name="static")
