import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

from src.config import DATA_URL_HISTO
from src.dashboard.theme import TEMPLATE, SIZE, COLOR_DISCRETE_SEQUENCE

### Config
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)


df = load_csv(DATA_URL_HISTO)
df["admission_date"] = pd.to_datetime(df["admission_date"])
df["réadmis"] = df["label"].map({
    0: "non",
    1: "oui"
})

# --- Tranches d'âge ---
bins = list(range(0, 105, 5))
labels = [f"{b}-{b+4}" for b in bins[:-1]]

df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)

# --- Comptage par genre ---
male   = df[df["gender"] == "Male"].groupby("age_group", observed=False)["patient_id"].count()
female = df[df["gender"] == "Female"].groupby("age_group", observed=False)["patient_id"].count()

male = male.reindex(labels, fill_value=0)
female = female.reindex(labels, fill_value=0)



# === PAGE STREAMLIT ===

st.title('Visualisation des données 📊')


col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown(f"### Distribution des patients par réadmission 🎯")
    fig = px.pie(
        df, 
        "réadmis",
        template = TEMPLATE,
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE
        )

    fig.update_layout(
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_droite:
    st.markdown(f"### Distribution des séjours patients par durée 🎯")
    fig = px.histogram(
        df, 
        x="length_of_stay",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Durée du séjour",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

### PROFIL DES PATIENTS ###

st.markdown("## Profil des patients 📋:")

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown(f"### Distribution des patients par genre 🧑‍⚕️")

    fig = px.histogram(
        df, 
        x="gender",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )
    
    fig.update_layout(
        xaxis_title="Genre",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_droite:
    st.markdown(f"### Distribution des patients par provenance géographique 🗺️")
    
    fig = px.histogram(
        df, 
        x="region",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )
    
    fig.update_layout(
        xaxis_title="Provenance géographique",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )
    st.plotly_chart(fig, width="stretch")



col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown(f"### Distribution des patients par âge 🎂")
    fig = px.histogram(
        df, 
        x="age",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )
    
    fig.update_layout(
        xaxis_title="Âge",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_droite:
    st.markdown(f"### Pyramide des âges 🎂")
        # --- Figure ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=-male.values,          # valeurs négatives → côté gauche
        name="Male",
        orientation="h",
        marker_color=COLOR_DISCRETE_SEQUENCE[0],
        customdata=male.values
    ))

    fig.add_trace(go.Bar(
        y=labels,
        x=female.values,
        name="Female",
        orientation="h",
        marker_color=COLOR_DISCRETE_SEQUENCE[1]
    ))

    # --- Mise en forme des ticks (valeurs absolues sur l'axe X) ---
    max_val = max(male.max(), female.max())
    step = 50
    ticks = list(range(0, max_val + step, step))
    tickvals = [-t for t in ticks[::-1] if t != 0] + ticks
    ticktext = [str(t) for t in ticks[::-1] if t != 0] + [str(t) for t in ticks]

    fig.update_layout(
        barmode="overlay",
        bargap=0.1,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            title="Nombre de patients",
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1.5
        ),
        yaxis=dict(title="Tranche d'âge"),
        legend=dict(x=0.87, y=0.02),
        template = TEMPLATE,
    )

    st.plotly_chart(fig, width="stretch")


### FLUX DES PATIENTS ###

st.markdown("## Flux des patients 📋:")

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown(f"### Distribution des patients par nombre de réadmissions précédentes 🕒")

    fig = px.histogram(
        df, 
        x="prev_readmissions",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Nombre de réadmissions précédentes",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_droite:
    st.markdown(f"### Distribution des admissions par saison ☀️")
    
    fig = px.histogram(
        df, 
        x="season",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Saison",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")







### DONNEES MEDICALES ###

st.markdown("## Données médicales 🩺:")

col_gauche, col_centre, col_droite = st.columns(3)

with col_gauche:
    st.markdown(f"### Distribution des patients par type de traitement 💉")

    fig = px.histogram(
        df, 
        x="treatment_type",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Type de traitement",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_centre:
    st.markdown(f"### Distribution des patients par nombre de comorbidités ⚠️")
    
    fig = px.histogram(
        df, 
        x="comorbidities_count",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Nombre de comorbidités",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

with col_droite:
    st.markdown(f"### Distribution des patients par nombre de médicaments 💊")
    
    fig = px.histogram(
        df, 
        x="medications_count",
        color = "réadmis",
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
        template = TEMPLATE
        )

    fig.update_layout(
        xaxis_title="Nombre de médicaments prescrits",
        yaxis_title="Nombre de patients",
        legend_title="Réadmission"
    )

    st.plotly_chart(fig, width="stretch")

st.markdown(f"### Distribution des patients par diagnostique principal 🧾")
fig = px.histogram(
    df, 
    x="primary_diagnosis",
    color = "réadmis",
    color_discrete_sequence=COLOR_DISCRETE_SEQUENCE,
    template = TEMPLATE
    )

fig.update_layout(
    xaxis_title="Diagnostique principal",
    yaxis_title="Nombre de patients",
    legend_title="Réadmission"
)

st.plotly_chart(fig, width="stretch")







