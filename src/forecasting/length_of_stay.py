"""Module M4 — prédiction de la durée de séjour et de la date de sortie."""

import numpy as np
import pandas as pd

from src.config import LENGTH_OF_STAY_FEATURE_COLUMNS
from src.services.prediction_api import call_length_of_stay_api

MIN_LENGTH_OF_STAY_DAYS = 1


def predict_length_of_stay(df_forecast, date_ref):
    """Ajoute `length_of_stay_prediction` et `discharge_date_prediction`.

    - Séjours terminés avant J : durée et date réelles (aucune prédiction).
    - Les autres (en cours à J, planning, réadmissions prédites) : durée prédite,
      arrondie au jour. Un patient déjà présent à J ne peut pas être sorti avant J :
      sa date de sortie est donc bornée à J (sans cela, le stock « réel » des jours
      précédant J était sous-estimé).
    """
    df = df_forecast.copy()
    date_ref = pd.Timestamp(date_ref)

    already_discharged = df["discharge_date"].notna() & (df["discharge_date"] < date_ref)
    to_predict = ~already_discharged

    df["length_of_stay_prediction"] = df["length_of_stay"].astype(float)
    df["discharge_date_prediction"] = df["discharge_date"]

    if to_predict.any():
        records = df.loc[to_predict, LENGTH_OF_STAY_FEATURE_COLUMNS].to_dict(orient="records")
        predicted_days = np.rint(np.asarray(call_length_of_stay_api(records), dtype=float))
        predicted_days = np.clip(predicted_days, MIN_LENGTH_OF_STAY_DAYS, None)

        admission = df.loc[to_predict, "admission_date"]
        discharge = (admission + pd.to_timedelta(predicted_days, unit="D")).clip(lower=date_ref)

        df.loc[to_predict, "discharge_date_prediction"] = discharge
        df.loc[to_predict, "length_of_stay_prediction"] = (discharge - admission).dt.days.astype(float)

    df["discharge_date_prediction"] = pd.to_datetime(df["discharge_date_prediction"])
    return df
