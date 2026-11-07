"""Module M8 — tableaux détaillés (sans donnée identifiante : RGPD, minimisation)."""

import streamlit as st

from src.data.privacy import pseudonymize


def render_census_table(df_inpatient):
    table = df_inpatient.rename(
        columns={
            "date": "Date",
            "initial_inpatient_census": "Effectif initial",
            "new_admissions": "Admissions",
            "new_readmissions": "Réadmissions",
            "inpatient_discharges": "Sorties",
            "final_inpatient_census": "Effectif final",
            "is_forecast": "Prévu",
        }
    )
    st.dataframe(table, hide_index=True, width="stretch")


def render_patient_table(df_patients):
    """Détail par séjour : identifiant pseudonymisé, aucune variable clinique ni démographique."""
    table = df_patients.assign(
        patient=pseudonymize(df_patients["patient_id"]),
        type=df_patients["label"].map({0: "Admission", 1: "Réadmission"}),
    )[
        [
            "patient",
            "type",
            "admission_date",
            "discharge_date_prediction",
            "length_of_stay_prediction",
        ]
    ].rename(
        columns={
            "patient": "Patient (pseudonyme)",
            "type": "Type",
            "admission_date": "Admission",
            "discharge_date_prediction": "Sortie (réelle ou prévue)",
            "length_of_stay_prediction": "Durée de séjour (j)",
        }
    )
    st.dataframe(table, hide_index=True, width="stretch")
