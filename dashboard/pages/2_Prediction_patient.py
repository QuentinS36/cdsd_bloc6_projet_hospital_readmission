"""Prédiction individuelle du risque de réadmission à 30 jours (appel à l'API)."""

import pandas as pd
import requests
import streamlit as st

from src.config import DATA_URL_HISTO
from src.data.loader import load_data
from src.services.prediction_api import call_readmission_api

st.set_page_config(page_title="Prédiction de réadmission", page_icon="🩺", layout="wide")


@st.cache_data(ttl=3600)
def load_options(source: str) -> pd.DataFrame:
    return load_data(source, "historical data")


st.title("🩺 Prédiction de la réadmission d'un patient")
st.caption(
    "Saisie à la sortie du patient. Aucune donnée saisie n'est enregistrée. "
    "Outil d'aide à la décision : il ne remplace pas le jugement clinique."
)

df = load_options(DATA_URL_HISTO)

col1, col2 = st.columns(2)

with col1:
    st.header("Informations générales")
    gender = st.selectbox("Sexe du patient", sorted(df["gender"].unique()))
    age = st.number_input("Âge du patient", min_value=0, max_value=110, value=65)
    region = st.selectbox("Région", sorted(df["region"].unique()))
    season = st.selectbox("Saison", sorted(df["season"].unique()))
    insurance_type = st.selectbox("Type d'assurance", sorted(df["insurance_type"].unique()))

with col2:
    st.header("Informations médicales")
    primary_diagnosis = st.selectbox("Diagnostic principal", sorted(df["primary_diagnosis"].unique()))
    treatment_type = st.selectbox("Type de traitement", sorted(df["treatment_type"].unique()))
    discharge_disposition = st.selectbox("Mode de sortie", sorted(df["discharge_disposition"].unique()))
    length_of_stay = st.slider("Durée du séjour (jours)", 1, 30, 8)
    comorbidities_count = st.slider("Nombre de comorbidités", 0, 20, 5)
    medications_count = st.slider("Nombre de médicaments", 0, 30, 8)
    followup_visits_last_year = st.slider("Visites de suivi l'année passée", 0, 20, 5)
    prev_readmissions = st.slider("Réadmissions passées", 0, 10, 1)

if st.button("Prédire la réadmission", type="primary"):
    features = {
        "season": season,
        "age": int(age),
        "gender": gender,
        "region": region,
        "primary_diagnosis": primary_diagnosis,
        "comorbidities_count": comorbidities_count,
        "length_of_stay": length_of_stay,
        "treatment_type": treatment_type,
        "medications_count": medications_count,
        "followup_visits_last_year": followup_visits_last_year,
        "prev_readmissions": prev_readmissions,
        "insurance_type": insurance_type,
        "discharge_disposition": discharge_disposition,
    }
    try:
        with st.spinner("Appel de l'API (jusqu'à ~1 min si elle se réveille)…"):
            prediction = call_readmission_api([features])[0]
    except requests.RequestException as exc:
        st.error(f"API injoignable ou en erreur ({type(exc).__name__}). Réessayez dans un instant.")
    else:
        if prediction == 1:
            st.error("Réadmission à 30 jours **prévue** : patient à surveiller.")
        else:
            st.success("Pas de réadmission à 30 jours prévue.")
