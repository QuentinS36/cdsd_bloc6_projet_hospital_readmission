"""Module M3 — prédiction des réadmissions (patients sortis à D-30)."""

from datetime import timedelta

import pandas as pd

from src.config import CHAINED_READMISSIONS, DELAY_READMISSION, READMISSION_FEATURE_COLUMNS
from src.services.prediction_api import call_readmission_api


def predict_readmissions(df_historical_data, date_ref, date_end):
    """Prédit, pour chaque jour de [J, date_end], les réadmissions des patients sortis 30 j avant.

    Un seul appel API est fait pour toute la période. Chaque patient prédit « réadmis »
    reçoit `admission_date = discharge_date + 30 j` (F03), `label = 1`, et un
    `prev_readmissions` incrémenté. La date de sortie est inconnue (NaT) : elle sera
    estimée par le modèle de durée de séjour.
    """
    empty = df_historical_data.iloc[0:0].copy()
    if df_historical_data.empty:
        return empty

    readmission_date = df_historical_data["discharge_date"].dt.normalize() + timedelta(
        days=DELAY_READMISSION
    )
    mask = (
        df_historical_data["discharge_date"].notna()
        & (readmission_date >= pd.Timestamp(date_ref))
        & (readmission_date <= pd.Timestamp(date_end))
    )
    if not CHAINED_READMISSIONS:
        mask &= df_historical_data["label"] == 0
    candidates = df_historical_data.loc[mask].copy()
    if candidates.empty:
        return empty

    predictions = call_readmission_api(
        candidates[READMISSION_FEATURE_COLUMNS].to_dict(orient="records")
    )
    candidates["readmission_prediction"] = predictions
    candidates["admission_date"] = readmission_date.loc[candidates.index]

    at_risk = candidates[candidates["readmission_prediction"] == 1].drop(
        columns=["readmission_prediction"]
    )
    at_risk["discharge_date"] = pd.NaT
    at_risk["prev_readmissions"] = at_risk["prev_readmissions"] + 1
    at_risk["label"] = 1
    return at_risk.reset_index(drop=True)
