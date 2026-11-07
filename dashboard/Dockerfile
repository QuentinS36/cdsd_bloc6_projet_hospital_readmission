FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

RUN useradd -m -u 1000 appuser
WORKDIR /app

COPY dashboard/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --chown=appuser dashboard/app.py .
COPY --chown=appuser dashboard/pages ./pages
COPY --chown=appuser dashboard/.streamlit ./.streamlit
COPY --chown=appuser src ./src
COPY --chown=appuser data/hospital_readmission_dataset.csv ./data/hospital_readmission_dataset.csv

USER appuser
EXPOSE 8501

# Render injecte $PORT ; 8501 en local.
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
