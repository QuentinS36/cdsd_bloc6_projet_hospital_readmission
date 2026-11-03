"""Page principale : pilotage de l'effectif hospitalier (J-30 → J+N)."""

import pandas as pd
import requests
import streamlit as st

from src.dashboard.kpis import render_kpi
from src.dashboard.sidebar import render_sidebar, render_sources_sidebar
from src.dashboard.tables import render_census_table, render_patient_table
from src.dashboard.visualisations import render_viz_bed_need, render_viz_census, render_viz_flow
from src.data.loader import load_data
from src.pipeline import build_forecast

st.set_page_config(page_title="Suivi Effectif Hospitalier", page_icon="🏥", layout="wide")


@st.cache_data(show_spinner="Chargement des données…", ttl=3600)
def cached_load(source: str, name: str) -> pd.DataFrame:
    return load_data(source, name)


@st.cache_data(
    show_spinner="Calcul de la prévision (appels à l'API de prédiction — "
    "jusqu'à ~1 min si l'API se réveille)…",
    ttl=3600,
)
def cached_forecast(
    histo_source, planning_source, date_ref, horizon, reduced_view, _df_hist, _df_planning
):
    # Les sources et paramètres servent de clé de cache : tout changement invalide le calcul.
    return build_forecast(_df_hist, _df_planning, date_ref, horizon, reduced_view)


def main():
    st.title("🏥 Suivi et prévision de l'effectif hospitalier")

    histo_source, planning_source = render_sources_sidebar()

    try:
        df_hist = cached_load(histo_source, "historical data")
    except ValueError as exc:
        st.error(f"Historique inutilisable : {exc}")
        st.stop()

    df_planning = None  # mode dégradé (F11) : historique seul
    if planning_source.strip():
        try:
            df_planning = cached_load(planning_source, "planning data")
        except ValueError as exc:
            st.warning(f"Planning inutilisable ({exc}) — mode dégradé : historique seul.")
    else:
        st.info("Aucun planning fourni — mode dégradé : historique seul.")

    params = render_sidebar(df_hist["admission_date"].min(), df_hist["admission_date"].max())

    try:
        result = cached_forecast(
            histo_source,
            planning_source,
            params["date_ref"],
            params["forecast_horizon_days"],
            params["reduced_view"],
            df_hist,
            df_planning,
        )
    except requests.RequestException as exc:
        st.error(
            "L'API de prédiction est injoignable ou a échoué. Sur l'offre gratuite Render, "
            "elle peut mettre ~1 minute à se réveiller : réessayez dans un instant.\n\n"
            f"Détail : {type(exc).__name__}"
        )
        st.stop()

    st.caption(
        f"Date de référence J = {result.date_ref:%d/%m/%Y} · affichage du "
        f"{result.date_start:%d/%m} au {result.date_end:%d/%m/%Y} · "
        "aide à la décision, ne se substitue pas au jugement clinique."
    )

    render_kpi(result.df_inpatient, params["capacity"], params["tolerance_range"])
    render_viz_census(
        result.df_inpatient, result.date_ref, params["reduced_view"], params["capacity"]
    )
    render_viz_flow(result.df_inpatient, result.date_ref)
    render_viz_bed_need(result.df_inpatient, params["capacity"])

    with st.expander("Détail journalier de l'effectif"):
        render_census_table(result.df_inpatient)
    with st.expander("Détail des séjours (identifiants pseudonymisés)"):
        render_patient_table(result.df_patients)


main()
