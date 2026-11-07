"""Barre latérale : sources de données et paramètres pilotables (cahier des charges §3.2)."""

from datetime import timedelta

import pandas as pd
import streamlit as st

from src.config import (
    CAPACITY,
    DATA_URL_HISTO,
    DATA_URL_PLANNING,
    DEFAULT_DATE,
    DEFAULT_HORIZON,
)


def render_sources_sidebar():
    """Sources de données (URL ou chemin). Retourne (url_historique, url_planning)."""
    st.sidebar.header("⚙️ Paramètres")
    st.sidebar.subheader("Sources de données")
    histo = st.sidebar.text_input("Historique des séjours (URL ou chemin CSV)", value=DATA_URL_HISTO)
    planning = st.sidebar.text_input(
        "Planning prévisionnel (vide = mode dégradé)", value=DATA_URL_PLANNING
    )
    return histo, planning


def render_sidebar(date_min, date_max):
    """Paramètres temporels et de capacité. Retourne le dictionnaire des choix."""
    st.sidebar.subheader("Paramètres temporels")

    default_date = min(max(pd.Timestamp(DEFAULT_DATE), date_min), date_max).date()
    date_ref = st.sidebar.date_input(
        "Date de référence",
        value=default_date,
        min_value=date_min.date(),
        max_value=date_max.date() + timedelta(days=1),
    )
    forecast_horizon_days = st.sidebar.slider(
        "Nombre de jours à prévoir", min_value=1, max_value=30, value=DEFAULT_HORIZON
    )
    reduced_view = st.sidebar.toggle("Vue réduite (J-7)", value=False)

    st.sidebar.subheader("Paramètres de capacité")
    capacity = st.sidebar.number_input("Capacité en lits", min_value=1, value=CAPACITY, step=1)
    tolerance_range = st.sidebar.slider(
        "Tolérance de capacité (%)", min_value=0, max_value=100, value=10, step=1
    )

    return {
        "date_ref": date_ref,
        "forecast_horizon_days": forecast_horizon_days,
        "reduced_view": reduced_view,
        "capacity": capacity,
        "tolerance_range": tolerance_range,
    }
