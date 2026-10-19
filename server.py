"""Server for the phone app: serves the app itself (static/) and the ML API.

Run locally:  .venv/bin/uvicorn server:app --port 8080   then open http://127.0.0.1:8080
On Cloud Run the Dockerfile starts this same command.
"""
import io
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from hydrangea import pruning, weather
from hydrangea.config import TASKS
from hydrangea.i18n import LANGS, M, t
from hydrangea.predict import analyse

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PHOTOS = 6
log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app):
    # Load CLIP + the text prompts before accepting traffic, so the first photo
    # isn't the one that waits for the model to load.
    from hydrangea import zeroshot
    from hydrangea.embed import _model

    _model()
    for task in TASKS:
        zeroshot.label_embeddings(task)
    log.info("model loaded")
    yield


app = FastAPI(title="Hydrangea Doctor", docs_url=None, redoc_url=None, lifespan=lifespan)


def error(status: int, key: str, lang: str, **params):
    return JSONResponse({"detail": t(key, lang, **params)}, status_code=status)


@app.get("/api/health")
def healthcheck():
    return {"ok": True}


@app.get("/api/species")
def species(lang: str = "en"):
    lang = lang if lang in LANGS else "en"
    return {s: t(f"species.{s}", lang) for s in pruning.SPECIES}


@app.post("/api/analyze")
async def analyze(
    photos: list[UploadFile] = File(...),
    species: str = Form("unknown"),
    age_years: float | None = Form(None),
    height_cm: float | None = Form(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    lang: str = Form("en"),
):
    lang = lang if lang in LANGS else "en"
    if species not in pruning.SPECIES:
        return error(400, "err_type", lang)
    if not 1 <= len(photos) <= MAX_PHOTOS:
        return error(400, "err_count", lang, max=MAX_PHOTOS)
    images = []
    for photo in photos:
        data = await photo.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            return error(413, "err_too_large", lang)
        try:
            image = Image.open(io.BytesIO(data))
            image.load()
        except (UnidentifiedImageError, OSError):
            return error(400, "err_not_photo", lang)
        images.append(image)

    w, weather_text = None, None
    if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
        try:
            w = weather.fetch_coords(lat, lon)
            weather_text = w.summary(lang)
        except Exception as e:  # weather is a bonus; never fail the whole request on it
            log.warning("weather failed: %s", e)
            weather_text = M("weather_failed").render(lang)

    r = analyse(images, species, height_cm=height_cm or None, age_years=age_years or None, weather=w)

    def task_json(res):
        return {"label": res.label, "text": t(f"label.{res.label}", lang), "confidence": res.confidence,
                "unsure": res.unsure, "method": res.method}

    return {
        **r["advice"].render(lang),
        "weather": weather_text,
        **{task: task_json(r[task]) for task in TASKS},
        "photos": [{task: task_json(photo[task]) for task in TASKS} for photo in r["photos"]],
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
