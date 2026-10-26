"""Server for the phone app: serves the app itself (static/) and the ML API.

Run locally:  .venv/bin/uvicorn server:app --port 8080   then open http://127.0.0.1:8080
On Cloud Run the Dockerfile starts this same command.
"""
import asyncio
import io
import json
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from hydrangea import chat, pruning, weather
from hydrangea.config import PLANTS
from hydrangea.i18n import LANGS, M, t

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PHOTOS = 6
log = logging.getLogger("uvicorn.error")


MODEL_TIMEOUT_S = 150
_ready = threading.Event()
_engine = {}


def _load_model():
    # Importing torch + loading CLIP takes ~30-40 s after the server wakes up.
    # Do it in the background so the page itself appears instantly; requests
    # that need the model wait for it (see _model_ready).
    from hydrangea import zeroshot
    from hydrangea.embed import _model
    from hydrangea.predict import NotAPlant, analyse

    _model()
    zeroshot.label_embeddings("plant")
    for plant in [*PLANTS, "unknown"]:
        for task in ("health", "stage"):
            zeroshot.label_embeddings(task, plant)
    zeroshot._presence_embeddings()
    _engine["analyse"], _engine["NotAPlant"] = analyse, NotAPlant
    _ready.set()
    log.info("model loaded")


@asynccontextmanager
async def lifespan(_app):
    threading.Thread(target=_load_model, daemon=True).start()
    yield


async def _model_ready() -> bool:
    return await asyncio.to_thread(_ready.wait, MODEL_TIMEOUT_S)


app = FastAPI(title="Hydrangea Doctor", docs_url=None, redoc_url=None, lifespan=lifespan)
# The GitHub Pages copy of the app calls this API from another origin.
app.add_middleware(CORSMiddleware, allow_origins=["https://aiyma-a.github.io"], allow_methods=["GET", "POST"], allow_headers=["*"])


def error(status: int, key: str, lang: str, **params):
    return JSONResponse({"detail": t(key, lang, **params)}, status_code=status)


@app.get("/api/health")
def healthcheck():
    return {"ok": True}


@app.get("/api/warmup")
async def warmup():
    """The app calls this as soon as it opens. Holding this request open also
    keeps Cloud Run's CPU switched on while the model loads in the background."""
    return {"ready": await _model_ready()}


@app.get("/api/species")
def species(lang: str = "en"):
    lang = lang if lang in LANGS else "en"
    return {s: t(f"species.{s}", lang) for s in pruning.SPECIES}


@app.get("/api/plants")
def plants(lang: str = "en"):
    lang = lang if lang in LANGS else "en"
    return {p: {"name": t(f"plant.{p}", lang), "kind": kind} for p, (_, kind) in PLANTS.items()}


@app.post("/api/analyze")
async def analyze(
    photos: list[UploadFile] = File(...),
    plant: str = Form("auto"),
    species: str = Form("unknown"),
    age_years: float | None = Form(None),
    ages: str | None = Form(None),  # JSON {plant: years}: the age of each plant the user told us about
    height_cm: float | None = Form(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    lang: str = Form("en"),
):
    lang = lang if lang in LANGS else "en"
    if species not in pruning.SPECIES or (plant not in ("auto", "unknown") and plant not in PLANTS):
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

    try:
        ages_by_plant = {k: float(v) for k, v in json.loads(ages).items() if k in PLANTS} if ages else {}
    except (ValueError, TypeError, AttributeError):
        ages_by_plant = {}
    if not await _model_ready():
        return error(503, "err_busy", lang)
    try:
        r = await asyncio.to_thread(_engine["analyse"], images, species, height_cm=height_cm or None, age_years=age_years or None, weather=w,
                                    plant=plant, ages=ages_by_plant)
    except _engine["NotAPlant"]:
        return JSONResponse({"detail": t("err_no_plant", lang), "code": "not_plant"}, status_code=422)

    def task_json(res, prefix="label"):
        return {"label": res.label, "text": t(f"{prefix}.{res.label}", lang), "confidence": res.confidence,
                "unsure": res.unsure, "method": res.method}

    return {
        **r["advice"].render(lang),
        "weather": weather_text,
        "plant": {**task_json(r["plant"], "plant"), "key": r["plant_key"], "text": t(f"plant.{r['plant_key']}", lang)},
        **{task: task_json(r[task]) for task in ("health", "stage")},
        "photos": [{task: task_json(photo[task]) for task in ("health", "stage")} for photo in r["photos"]],
    }


@app.post("/api/identify")
async def identify_endpoint(request: Request, photos: list[UploadFile] = File(...), lang: str = Form("en")):
    lang = lang if lang in LANGS else "en"
    if not 1 <= len(photos) <= chat.MAX_ID_PHOTOS:
        return error(400, "err_count", lang, max=chat.MAX_ID_PHOTOS)
    jpegs = []
    for photo in photos:
        data = await photo.read(MAX_UPLOAD_BYTES + 1)
        try:
            image = Image.open(io.BytesIO(data))
            image.load()
        except (UnidentifiedImageError, OSError):
            return error(400, "err_not_photo", lang)
        image = image.convert("RGB")
        image.thumbnail((1024, 1024))
        out = io.BytesIO()
        image.save(out, "JPEG", quality=85)
        jpegs.append(out.getvalue())
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")).split(",")[0].strip()
    candidates = {k: t(f"plant.{k}", "en") for k in PLANTS}
    try:
        return await asyncio.to_thread(chat.identify, jpegs, lang, candidates, ip)
    except chat.RateLimited:
        return error(429, "err_chat_limit", lang)
    except chat.ChatUnavailable as e:
        log.warning("identify failed: %s", e)
        return error(503, "err_chat", lang)


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
    except ValueError:
        body = None
    body = body if isinstance(body, dict) else {}
    lang = body.get("lang") if body.get("lang") in LANGS else "en"
    question = body.get("question")
    if not isinstance(question, str) or not question.strip() or len(question) > chat.MAX_QUESTION:
        return error(400, "err_question", lang)
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")).split(",")[0].strip()
    try:
        reply = await asyncio.to_thread(chat.ask, question.strip(), body.get("context"), body.get("history"), lang, ip)
    except chat.RateLimited:
        return error(429, "err_chat_limit", lang)
    except chat.ChatUnavailable as e:
        log.warning("chat failed: %s", e)
        return error(503, "err_chat", lang)
    return {"reply": reply}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
