"""Chargement des jeux de données (chemin local ou URL ; CSV ou XLSX)."""

import pandas as pd

from src.data.validation import validate_dataset, validate_temporal_consistency


def _read(source: str) -> pd.DataFrame:
    if str(source).lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(source)
    return pd.read_csv(source)


def load_data(source: str, dataset_name: str = "dataset") -> pd.DataFrame:
    """Charge un fichier, le valide et calcule `discharge_date`.

    Lève ValueError avec un message explicite si la source est vide, illisible
    ou non conforme au schéma attendu (exigence F01).
    """
    if not source or not str(source).strip():
        raise ValueError("Merci de bien vouloir renseigner une source de données valide.")

    try:
        df = _read(str(source).strip())
    except Exception as exc:
        raise ValueError(f"Unable to read data from: {source} ({exc})") from exc

    validate_dataset(df, dataset_name)

    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["length_of_stay"] = pd.to_numeric(df["length_of_stay"], errors="coerce")
    if df["length_of_stay"].isna().any():
        raise ValueError("Column 'length_of_stay' contains non-numeric values.")
    df["discharge_date"] = df["admission_date"] + pd.to_timedelta(df["length_of_stay"], unit="D")
    validate_temporal_consistency(df)
    return df


def load_historical_data(source: str) -> pd.DataFrame:
    return load_data(source, "historical data")


def load_planning_data(source: str) -> pd.DataFrame:
    return load_data(source, "planning data")
