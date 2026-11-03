"""Préparation des données : fenêtres temporelles, réadmissions historiques, planning."""

from datetime import timedelta

import pandas as pd

from src.config import (
    DELAY_READMISSION,
    FULL_VIEW_DAYS,
    HISTORICAL_WINDOW_DAYS,
    REDUCED_VIEW_DAYS,
)


def prepare_forecast_period(date_ref, forecast_horizon_days, reduced_view, date_min):
    """Calcule (date J, début de l'affichage, fin de l'horizon de prévision)."""
    date_ref = pd.Timestamp(date_ref)
    date_end = date_ref + timedelta(days=forecast_horizon_days - 1)
    view_days = REDUCED_VIEW_DAYS if reduced_view else FULL_VIEW_DAYS
    date_start = max(date_ref - timedelta(days=view_days), pd.Timestamp(date_min))
    return date_ref, date_start, date_end


def prepare_historical_admissions(df_historique, date_ref):
    """Admissions de la fenêtre [J - fenêtre, J[ (label = 0 : simple admission)."""
    start_date = date_ref - timedelta(days=HISTORICAL_WINDOW_DAYS)
    mask = (df_historique["admission_date"] >= start_date) & (
        df_historique["admission_date"] < date_ref
    )
    df_histo = df_historique.loc[mask].copy()
    df_histo["label"] = 0
    return df_histo


def prepare_historical_readmissions(df_historique, date_ref):
    """Réadmissions *constatées* dans [J - fenêtre, J[.

    Un séjour avec label = 1 donne lieu à une réadmission à `discharge_date + 30 j`
    (même règle que pour les réadmissions prédites — exigence F03). La durée du
    séjour de réadmission est approximée par celle du séjour d'origine. Ne modifie
    pas le DataFrame d'entrée.
    """
    start_date = date_ref - timedelta(days=HISTORICAL_WINDOW_DAYS)

    df = df_historique.loc[df_historique["label"] == 1].copy()
    df["admission_date"] = df["discharge_date"] + timedelta(days=DELAY_READMISSION)
    df["discharge_date"] = df["admission_date"] + pd.to_timedelta(df["length_of_stay"], unit="D")
    df["prev_readmissions"] = df["prev_readmissions"] + 1

    mask = (df["admission_date"] >= start_date) & (df["admission_date"] < date_ref)
    return df.loc[mask].copy()


def prepare_historical_data(df_histo, df_read_histo):
    """Combine admissions et réadmissions historiques."""
    return pd.concat([df_histo, df_read_histo], ignore_index=True)


def prepare_planning(df_planning, date_ref, date_end):
    """Admissions programmées dans [J, J+N-1].

    Ce sont des admissions planifiées : `label` est forcé à 0 (le fichier source
    contient l'issue réelle, qu'un vrai planning ne connaîtrait pas).
    """
    mask = (df_planning["admission_date"] >= date_ref) & (df_planning["admission_date"] <= date_end)
    df = df_planning.loc[mask].copy()
    df["label"] = 0
    return df


def prepare_forecast_data(df_historical_data, df_planning, df_readmission_predictions):
    """Combine historique, planning et réadmissions prédites."""
    frames = [f for f in (df_historical_data, df_planning, df_readmission_predictions) if not f.empty]
    return pd.concat(frames, ignore_index=True)
