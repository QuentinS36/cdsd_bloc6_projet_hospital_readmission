"""Enchaînement complet de la prévision d'effectif (M1 → M5), sans dépendance à Streamlit.

historique + planning  ->  réadmissions prédites (API)  ->  durées de séjour prédites (API)
                       ->  effectif journalier [J-30 ; J+N]
"""

from dataclasses import dataclass

import pandas as pd

from src.business.inpatient import inpatient_census
from src.data.data_processing import (
    prepare_forecast_data,
    prepare_forecast_period,
    prepare_historical_admissions,
    prepare_historical_data,
    prepare_historical_readmissions,
    prepare_planning,
)
from src.forecasting.length_of_stay import predict_length_of_stay
from src.forecasting.readmission import predict_readmissions


@dataclass
class ForecastResult:
    date_ref: pd.Timestamp
    date_start: pd.Timestamp
    date_end: pd.Timestamp
    df_inpatient: pd.DataFrame  # effectif journalier
    df_patients: pd.DataFrame  # détail patient (à pseudonymiser avant affichage)


def build_forecast(
    df_historic_raw: pd.DataFrame,
    df_planning_raw: pd.DataFrame | None,
    date_ref,
    forecast_horizon_days: int,
    reduced_view: bool,
) -> ForecastResult:
    """Construit la prévision. `df_planning_raw=None` active le mode dégradé (F11)."""
    date_min = df_historic_raw["admission_date"].min()
    date_ref, date_start, date_end = prepare_forecast_period(
        date_ref, forecast_horizon_days, reduced_view, date_min
    )

    if df_planning_raw is None:
        df_planning_raw = df_historic_raw.iloc[0:0]

    df_hist = prepare_historical_data(
        prepare_historical_admissions(df_historic_raw, date_ref),
        prepare_historical_readmissions(df_historic_raw, date_ref),
    )
    df_planning = prepare_planning(df_planning_raw, date_ref, date_end)
    df_readmissions = predict_readmissions(df_hist, date_ref, date_end)

    df_forecast = prepare_forecast_data(df_hist, df_planning, df_readmissions)
    df_final = predict_length_of_stay(df_forecast, date_ref)
    df_inpatient = inpatient_census(df_final, date_ref, date_start, date_end)

    return ForecastResult(date_ref, date_start, date_end, df_inpatient, df_final)
