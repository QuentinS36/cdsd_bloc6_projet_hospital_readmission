"""Chargement des modèles côté API.

Ordre de résolution :
1. Registre MLflow hébergé sur DagsHub (si les variables d'environnement sont définies) ;
2. à défaut (ou en cas d'échec), dossier local `models/<nom_du_modèle>` produit par
   `scripts/export_models.py` — procédure de repli prévue dans la note de cadrage.

L'authentification DagsHub passe par les variables standard de MLflow
(MLFLOW_TRACKING_USERNAME / MLFLOW_TRACKING_PASSWORD) : pas de connexion
interactive (`dagshub.init`) qui bloquerait un serveur sans terminal.
"""

import logging
import os
from dataclasses import dataclass

from src import config

logger = logging.getLogger(__name__)


@dataclass
class LoadedModel:
    model: object
    source: str


def configure_mlflow() -> bool:
    """Configure MLflow depuis l'environnement. Retourne False si rien n'est défini."""
    import mlflow

    uri = os.getenv("MLFLOW_TRACKING_URI")
    if not uri and config.DAGSHUB_OWNER and config.DAGSHUB_REPO:
        uri = f"https://dagshub.com/{config.DAGSHUB_OWNER}/{config.DAGSHUB_REPO}.mlflow"
        os.environ.setdefault("MLFLOW_TRACKING_USERNAME", config.DAGSHUB_OWNER)
        if config.DAGSHUB_USER_TOKEN:
            os.environ.setdefault("MLFLOW_TRACKING_PASSWORD", config.DAGSHUB_USER_TOKEN)
    if not uri:
        return False
    mlflow.set_tracking_uri(uri)
    return True


def load_model(name: str, version: str) -> LoadedModel:
    import mlflow.sklearn

    errors: list[str] = []

    if configure_mlflow():
        uri = f"models:/{name}/{version}"
        try:
            return LoadedModel(mlflow.sklearn.load_model(uri), f"registry:{uri}")
        except Exception as exc:  # réseau, droits, version inexistante...
            logger.warning("Registre MLflow indisponible pour %s : %s", uri, exc)
            errors.append(f"registre ({type(exc).__name__})")
    else:
        errors.append("registre non configuré")

    local_path = config.LOCAL_MODELS_DIR / name
    if local_path.exists():
        return LoadedModel(mlflow.sklearn.load_model(str(local_path)), f"local:{local_path}")
    errors.append(f"dossier local absent ({local_path})")

    raise RuntimeError(f"Impossible de charger le modèle '{name}' : {' ; '.join(errors)}")


def load_models() -> dict[str, LoadedModel]:
    return {
        "readmission": load_model(
            config.READMISSION_MODEL_NAME, config.READMISSION_MODEL_VERSION
        ),
        "length_of_stay": load_model(
            config.LENGTH_OF_STAY_MODEL_NAME, config.LENGTH_OF_STAY_MODEL_VERSION
        ),
    }
