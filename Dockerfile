# Image for Google Cloud Run: the ML server + the phone app.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 HF_HOME=/app/.hf PIP_NO_CACHE_DIR=1
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision \
 && pip install transformers scikit-learn joblib pillow fastapi uvicorn python-multipart matplotlib
# Download CLIP at build time so the app doesn't fetch 600 MB on every cold start.
RUN python -c "from transformers import CLIPModel, CLIPProcessor; m='openai/clip-vit-base-patch32'; CLIPModel.from_pretrained(m); CLIPProcessor.from_pretrained(m)"
COPY hydrangea/ hydrangea/
COPY static/ static/
COPY models/ models/
COPY server.py .
ENV HF_HUB_OFFLINE=1
RUN useradd -m app && chown -R app /app
USER app
CMD exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}
