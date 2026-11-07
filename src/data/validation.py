"""Contrôles qualité à l'ingestion (cahier des charges §4.3, exigence F01)."""

import pandas as pd

from src import config


def validate_required_columns(df: pd.DataFrame, required_columns) -> None:
    """Vérifie que toutes les colonnes requises sont présentes."""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")


def validate_not_empty(df: pd.DataFrame, dataset_name: str = "dataset") -> None:
    if df.empty:
        raise ValueError(f"The {dataset_name} is empty.")


def validate_date_column(df: pd.DataFrame, column_name: str) -> None:
    """Toutes les dates doivent être valides (échec explicite sinon)."""
    if column_name not in df.columns:
        raise ValueError(f"Missing date column: '{column_name}'.")
    invalid = pd.to_datetime(df[column_name], errors="coerce").isna().sum()
    if invalid:
        raise ValueError(f"Column '{column_name}' contains {invalid} invalid date(s).")


def validate_no_missing(df: pd.DataFrame, columns) -> None:
    """Valeurs manquantes sur les colonnes utilisées par les modèles (§4.3)."""
    counts = df[list(columns)].isna().sum()
    counts = counts[counts > 0]
    if not counts.empty:
        raise ValueError(f"Missing values in model columns: {counts.to_dict()}")


def validate_temporal_consistency(df: pd.DataFrame) -> None:
    """discharge_date doit être postérieure ou égale à admission_date."""
    if (df["discharge_date"] < df["admission_date"]).any():
        raise ValueError("Some discharge_date values precede admission_date.")


def validate_dataset(df: pd.DataFrame, dataset_name: str = "dataset") -> None:
    """Validation complète d'un fichier historique ou planning."""
    validate_not_empty(df, dataset_name)
    validate_required_columns(df, config.REQUIRED_DATA_COLUMNS)
    validate_date_column(df, "admission_date")
    validate_no_missing(
        df,
        set(config.READMISSION_FEATURE_COLUMNS) | set(config.LENGTH_OF_STAY_FEATURE_COLUMNS),
    )


# Alias conservés (anciens noms)
validate_historical_data = validate_planning_data = validate_readmission_history = validate_dataset
