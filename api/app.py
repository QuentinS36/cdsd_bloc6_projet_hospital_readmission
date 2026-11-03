"""API FastAPI : prédiction de la réadmission à 30 jours et de la durée de séjour.

Les modèles sont chargés une seule fois au démarrage (registre MLflow/DagsHub,
ou dossier local de repli). Aucune donnée patient n'est journalisée : seuls
des volumes sont tracés (RGPD, art. 5 et 9).
"""

import logging
import secrets
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from src import config
from src.services import model_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hospital_api")

MAX_BATCH_SIZE = 5000


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models = None
    app.state.load_error = None
    try:
        app.state.models = model_registry.load_models()
        for key, loaded in app.state.models.items():
            logger.info("Modèle '%s' chargé depuis %s", key, loaded.source)
    except Exception as exc:  # l'API démarre quand même : /healthz renverra 503
        app.state.load_error = str(exc)
        logger.exception("Chargement des modèles impossible.")
    yield


app = FastAPI(
    title="Hospital Readmission API",
    description="API de prédiction de la réadmission du patient et de sa durée de séjour",
    version="1.1.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# Sécurité : clé d'API optionnelle (header X-API-Key)
# ─────────────────────────────────────────────
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = config.API_KEY
    if expected and not (x_api_key and secrets.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def get_model(request: Request, key: str):
    models = request.app.state.models
    if models is None:
        raise HTTPException(status_code=503, detail="Models are not loaded.")
    return models[key].model


# ─────────────────────────────────────────────
# Schémas
# ─────────────────────────────────────────────
class _Patient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season: str
    age: int = Field(ge=0, le=120)
    gender: str
    region: str
    primary_diagnosis: str
    comorbidities_count: int = Field(ge=0, le=50)
    treatment_type: str
    medications_count: int = Field(ge=0, le=100)
    followup_visits_last_year: int = Field(ge=0, le=100)
    prev_readmissions: int = Field(ge=0, le=100)
    insurance_type: str


class ReadmissionFeatures(_Patient):
    """Caractéristiques d'un patient à la sortie."""

    length_of_stay: int = Field(ge=0, le=365)
    discharge_disposition: str


class LengthOfStayFeatures(_Patient):
    """Caractéristiques d'un patient à l'admission."""


class ReadmissionRequest(BaseModel):
    readmissions: list[ReadmissionFeatures] = Field(max_length=MAX_BATCH_SIZE)


class LengthOfStayRequest(BaseModel):
    lengths_of_stay: list[LengthOfStayFeatures] = Field(max_length=MAX_BATCH_SIZE)


class PredictionResponse(BaseModel):
    predictions: list[float]


ReadmissionResponse = LengthOfStayResponse = PredictionResponse


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def healthcheck() -> dict[str, str]:
    """Liveness : l'application répond."""
    return {"status": "ok"}


@app.get("/healthz", tags=["Health"])
def readiness(request: Request):
    """Readiness : 200 seulement si les deux modèles sont chargés (utilisé par Render)."""
    models = request.app.state.models
    if models is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Loading")
    return {"status": "ok", "models": {k: v.source for k, v in models.items()}}


def _predict(model, rows: list[BaseModel], columns: list[str]) -> PredictionResponse:
    try:
        dataframe = pd.DataFrame([row.model_dump() for row in rows], columns=columns)
        predictions = model.predict(dataframe)
    except Exception as exc:
        logger.exception("Prediction failed (%d rows).", len(rows))
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc
    logger.info("Prediction OK (%d rows).", len(rows))
    return PredictionResponse(predictions=[float(v) for v in predictions])


@app.post(
    "/_readmission_predict",
    response_model=ReadmissionResponse,
    tags=["Prediction"],
    dependencies=[Depends(require_api_key)],
)
def readmission_predict(payload: ReadmissionRequest, request: Request) -> ReadmissionResponse:
    """Prédit la réadmission (1.0 = réadmis à 30 jours, 0.0 = non) pour une liste de patients."""
    return _predict(
        get_model(request, "readmission"),
        payload.readmissions,
        config.READMISSION_FEATURE_COLUMNS,
    )


@app.post(
    "/_length_of_stay_predict",
    response_model=LengthOfStayResponse,
    tags=["Prediction"],
    dependencies=[Depends(require_api_key)],
)
def length_of_stay_predict(payload: LengthOfStayRequest, request: Request) -> LengthOfStayResponse:
    """Prédit la durée de séjour (jours) pour une liste de patients."""
    return _predict(
        get_model(request, "length_of_stay"),
        payload.lengths_of_stay,
        config.LENGTH_OF_STAY_FEATURE_COLUMNS,
    )
