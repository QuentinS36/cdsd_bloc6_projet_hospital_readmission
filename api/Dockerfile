FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# libgomp1 : requis par xgboost (absent de l'image slim)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --chown=appuser api/app.py .
COPY --chown=appuser src ./src
COPY --chown=appuser models ./models

USER appuser
EXPOSE 8000

# Render injecte $PORT (10000 par défaut) ; 8000 en local.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
