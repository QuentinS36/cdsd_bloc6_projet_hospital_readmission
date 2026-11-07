"""Configuration centralisée du projet.

Aucune valeur secrète n'est écrite ici : tout vient des variables d'environnement
(fichier `.env` en local, variables du service sur Render / Docker).
Aucune variable n'est obligatoire à l'import : l'API et le dashboard ne
demandent chacun que ce dont ils ont besoin.
"""

import os
from pathlib import Path

try:  # python-dotenv n'est installé qu'en local (pas dans les images de prod)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _normalize_url(url: str) -> str:
    """Ajoute https:// si absent et retire le '/' final (utile avec Render)."""
    url = url.strip().rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


# ─────────────────────────────────────────────
# Données (chemin local par défaut, URL possible)
# ─────────────────────────────────────────────
_DEFAULT_DATA = str(PROJECT_ROOT / "data" / "hospital_readmission_dataset.csv")
DATA_URL_HISTO = os.getenv("DATA_URL_HISTO", _DEFAULT_DATA)
# Le planning est simulé à partir du même jeu (admissions postérieures à la date J)
DATA_URL_PLANNING = os.getenv("DATA_URL_PLANNING", _DEFAULT_DATA)

# ─────────────────────────────────────────────
# Métier
# ─────────────────────────────────────────────
DEFAULT_DATE = "2023-07-01"  # date J par défaut de la démo
DEFAULT_HORIZON = 7  # nombre de jours prévus par défaut
CAPACITY = 80  # capacité nominale par défaut (ajustable dans l'interface)
HISTORICAL_WINDOW_DAYS = 60  # fenêtre d'historique avant J
REDUCED_VIEW_DAYS = 7
FULL_VIEW_DAYS = 30
DELAY_READMISSION = 30  # délai de réadmission en jours (sortie + 30 j)
# Si False (défaut), seules les admissions « d'origine » peuvent déclencher une réadmission
# prédite, comme dans l'historique constaté (une ligne du jeu = un séjour, une issue).
# Si True, un séjour de réadmission peut lui-même être suivi d'une réadmission (chaînage).
CHAINED_READMISSIONS = os.getenv("CHAINED_READMISSIONS", "false").lower() == "true"

ALERT_DAY_THRESHOLD = 1  # alerte si le nombre de jours en saturation / sous-occupation est > 1 (F07)

RANDOM_STATE = 42

# ─────────────────────────────────────────────
# MLflow / DagsHub (utilisé par l'API et les notebooks)
# ─────────────────────────────────────────────
DAGSHUB_OWNER = os.getenv("DAGSHUB_OWNER")
DAGSHUB_REPO = os.getenv("DAGSHUB_REPO")
DAGSHUB_USER_TOKEN = os.getenv("DAGSHUB_USER_TOKEN")

# Dossier de repli : modèles MLflow exportés (voir scripts/export_models.py)
LOCAL_MODELS_DIR = Path(os.getenv("LOCAL_MODELS_DIR", PROJECT_ROOT / "models"))

READMISSION_MODEL_NAME = "readmission_prediction"
READMISSION_MODEL_VERSION = os.getenv("READMISSION_MODEL_VERSION", "1")
READMISSION_FEATURE_COLUMNS = [
    "season",
    "age",
    "gender",
    "region",
    "primary_diagnosis",
    "comorbidities_count",
    "length_of_stay",
    "treatment_type",
    "medications_count",
    "followup_visits_last_year",
    "prev_readmissions",
    "insurance_type",
    "discharge_disposition",
]

LENGTH_OF_STAY_MODEL_NAME = "length_of_stay_prediction"
LENGTH_OF_STAY_MODEL_VERSION = os.getenv("LENGTH_OF_STAY_MODEL_VERSION", "1")
LENGTH_OF_STAY_FEATURE_COLUMNS = [
    "season",
    "age",
    "gender",
    "region",
    "primary_diagnosis",
    "comorbidities_count",
    "treatment_type",
    "medications_count",
    "followup_visits_last_year",
    "prev_readmissions",
    "insurance_type",
]

# Colonnes minimales attendues dans les fichiers historique / planning
REQUIRED_DATA_COLUMNS = sorted(
    {"patient_id", "admission_date", "length_of_stay", "label"}
    | set(READMISSION_FEATURE_COLUMNS)
    | set(LENGTH_OF_STAY_FEATURE_COLUMNS)
)

# ─────────────────────────────────────────────
# Dashboard -> API
# ─────────────────────────────────────────────
API_URL = _normalize_url(os.getenv("API_URL", "http://localhost:8000"))
API_KEY = os.getenv("API_KEY")  # optionnelle : si définie côté API, requise partout
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "90"))

# ─────────────────────────────────────────────
# RGPD : sel de pseudonymisation des identifiants affichés
# (aléatoire par processus si non défini)
# ─────────────────────────────────────────────
PSEUDONYMIZATION_SALT = os.getenv("PSEUDONYMIZATION_SALT")
