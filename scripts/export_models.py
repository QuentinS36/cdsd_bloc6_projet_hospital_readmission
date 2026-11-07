"""Exporte les modèles du registre DagsHub vers `models/` (procédure de repli).

Usage :  python scripts/export_models.py
Nécessite DAGSHUB_OWNER, DAGSHUB_REPO et DAGSHUB_USER_TOKEN dans l'environnement ou le .env.
Le dossier `models/` peut ensuite être monté / copié dans l'image de l'API : si le registre
est injoignable, l'API charge ces copies locales (même version = même comportement).
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow.sklearn  # noqa: E402

from src import config  # noqa: E402
from src.services.model_registry import configure_mlflow  # noqa: E402

MODELS = {
    config.READMISSION_MODEL_NAME: config.READMISSION_MODEL_VERSION,
    config.LENGTH_OF_STAY_MODEL_NAME: config.LENGTH_OF_STAY_MODEL_VERSION,
}


def main() -> None:
    if not configure_mlflow():
        sys.exit("Définir DAGSHUB_OWNER / DAGSHUB_REPO (ou MLFLOW_TRACKING_URI).")
    for name, version in MODELS.items():
        target = config.LOCAL_MODELS_DIR / name
        if target.exists():
            shutil.rmtree(target)
        model = mlflow.sklearn.load_model(f"models:/{name}/{version}")
        mlflow.sklearn.save_model(model, str(target), serialization_format="cloudpickle")
        print(f"✓ {name} v{version} -> {target}")


if __name__ == "__main__":
    main()
