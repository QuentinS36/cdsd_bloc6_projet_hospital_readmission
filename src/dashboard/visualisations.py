import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.business.inpatient import (
    calculate_kpi
)
from src.dashboard.theme import COLOR_DISCRETE_SEQUENCE

def render_viz_census(
        df_inpatient, 
        date_ref, 
        reduced_view,
        capacity,
    ):
    """
    Viz 1 — Stacked area chart effectif journalier
    Zone is_forecast == True affichée en transparence réduite
    """
    fig = go.Figure()
 
    avg_inpatient, _, _ = calculate_kpi(
        df_inpatient
    ) 

    title = "J → J+7" if reduced_view else "J-30 → J+7"
 
    # ── Hover unifié invisible ──
    fig.add_trace(go.Bar(
        x=df_inpatient["date"],
        y=df_inpatient["final_inpatient_census"],
        name="",
        marker=dict(color="rgba(0,0,0,0)", opacity=0),
        showlegend=False,
        customdata=list(zip(
            df_inpatient["initial_inpatient_census"],
            df_inpatient["new_admissions"],
            df_inpatient["new_readmissions"],
            df_inpatient["final_inpatient_census"],
            df_inpatient["is_forecast"].map({True: "(prévu)", False: ""}),
        )),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b>"
            " %{customdata[4]}<br>"
            "Effectif initial : <b>%{customdata[0]}</b><br>"
            "Admissions : <b>%{customdata[1]}</b><br>"
            "Réadmissions : <b>%{customdata[2]}</b><br>"
            "──────────────<br>"
            "Effectif final : <b>%{customdata[3]}</b>"
            "<extra></extra>"
        ),
    ))
 
    # ── Données réelles ──
    mask_forecast = df_inpatient["is_forecast"]

    df_reel     = df_inpatient[~mask_forecast].copy()
    df_forecast = df_inpatient[mask_forecast].copy()

    if not df_reel.empty and not df_forecast.empty:
        # on ajoute le dernier point réel au début de la série prévue
        # pour que les deux zones se rejoignent visuellement
        pont = df_reel.iloc[[-1]]
        df_forecast = pd.concat([pont, df_forecast], ignore_index=True)

 
    for df, opacity, suffix in [
        (df_reel,     0.7, ""),
        (df_forecast, 0.9, " (prévu)"),
    ]:
        if df.empty:
            continue
 
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["initial_inpatient_census"],
            name=f"Effectif initial{suffix}",
            mode="lines", stackgroup=f"one{'_f' if suffix else ''}",
            fillcolor=f"rgba(1, 78, 151, {opacity})",
            line=dict(color=f"rgba(1, 78, 151, {opacity + 0.1})", width=2),
            hoverinfo="skip",
            showlegend=not bool(suffix),
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["new_admissions"],
            name=f"Admissions{suffix}",
            mode="lines", stackgroup=f"one{'_f' if suffix else ''}",
            fillcolor=f"rgba(65, 184, 213, {opacity})",
            line=dict(color=f"rgba(65, 184, 213, {opacity + 0.1})", width=2),
            hoverinfo="skip",
            showlegend=not bool(suffix),
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["new_readmissions"],
            name=f"Réadmissions{suffix}",
            mode="lines", stackgroup=f"one{'_f' if suffix else ''}",
            fillcolor=f"rgba(255,80,80, {opacity})",
            line=dict(color=f"rgba(255,80,80, {opacity + 0.1})", width=2),
            hoverinfo="skip",
            showlegend=not bool(suffix),
        ))
 
    # ── Lignes horizontales ──
    fig.add_hline(
        y=capacity, line_dash="dash", line_color="red", line_width=3,
        annotation_text=f"Capacité ({capacity})",
        annotation_position="top left",
        annotation_bgcolor="rgba(0,0,0,0.6)",
        annotation_font_color="white", annotation_font_size=11,
    )
    fig.add_hline(
        y=avg_inpatient, line_dash="dash",
        line_color="rgba(54, 222, 54, 0.8)", line_width=3,
        annotation_text=f"Moy. période ({avg_inpatient:.0f})",
        annotation_position="top right",
        annotation_bgcolor="rgba(0,0,0,0.6)",
        annotation_font_color="white", annotation_font_size=11,
    )
 
    # ── Ligne verticale J ──
    fig.add_shape(
        type="line",
        x0=date_ref.strftime("%Y-%m-%d"), x1=date_ref.strftime("%Y-%m-%d"),
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="rgba(255,255,255,0.6)", width=4, dash="dot"),
    )
    fig.add_annotation(
        x=date_ref.strftime("%Y-%m-%d"), y=1,
        xref="x", yref="paper",
        text=f"J ({date_ref.strftime('%d %b')})",
        showarrow=False, font=dict(color="white", size=11), yanchor="bottom",
    )
 
    fig.update_layout(
        title=f"Effectif journalier",
        xaxis_title="Date", yaxis_title="Nombre de patients",
        hovermode="x",
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_size=13, font_color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", rangemode="tozero"),
        height=500,
    )
 
    st.plotly_chart(fig, width="stretch")


def render_viz_flow(
        df_inpatient,
        date_ref,
):
    """
    Viz 2 — Flux journalier entrées / sorties
    """

    fig = go.Figure()
 
    # ── Hover unifié invisible ──
    fig.add_trace(go.Bar(
        x=df_inpatient["date"],
        y=df_inpatient["new_admissions"] + df_inpatient["new_readmissions"],
        name="",
        marker=dict(color="rgba(0,0,0,0)", opacity=0),
        showlegend=False,
        customdata=list(zip(
            df_inpatient["new_admissions"] + df_inpatient["new_readmissions"],
            df_inpatient["inpatient_discharges"],
            (df_inpatient["new_admissions"] + df_inpatient["new_readmissions"]) - df_inpatient["inpatient_discharges"],
        )),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            "Entrées : <b>%{customdata[0]}</b><br>"
            "Sorties : <b>%{customdata[1]}</b><br>"
            "──────────────<br>"
            "Solde : <b>%{customdata[2]:+d}</b>"
            "<extra></extra>"
        ),
    ))

    entrees = df_inpatient["new_admissions"] + df_inpatient["new_readmissions"]
 
    # ── Courbe entrées ──
    fig.add_trace(go.Scatter(
        x=df_inpatient["date"], y=entrees,
        name="Entrées (Patients admis + patients réadmis)",
        mode="lines+markers",
        line=dict(color=COLOR_DISCRETE_SEQUENCE[2], width=2),
        marker=dict(size=4),
        hoverinfo="skip",
    ))
 
    # ── Courbe sorties ──
    fig.add_trace(go.Scatter(
        x=df_inpatient["date"], y=df_inpatient["inpatient_discharges"],
        name="Sorties",
        mode="lines+markers",
        line=dict(color="rgba(255,80,80,1)", width=2),
        marker=dict(size=4),
        hoverinfo="skip",
    ))
 
    # ── Ligne verticale J ──
    fig.add_shape(
        type="line",
        x0=date_ref.strftime("%Y-%m-%d"), x1=date_ref.strftime("%Y-%m-%d"),
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="rgba(255,255,255,0.6)", width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=date_ref.strftime("%Y-%m-%d"), y=1,
        xref="x", yref="paper",
        text=f"J ({date_ref.strftime('%d %b')})",
        showarrow=False, font=dict(color="white", size=11), yanchor="bottom",
    )
 
    fig.update_layout(
        title=f"Flux journalier Entrées / Sorties",
        xaxis_title="Date", yaxis_title="Nombre de patients",
        hovermode="x",
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_size=13, font_color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", rangemode="tozero"),
        height=400,
    )
 
    st.plotly_chart(fig, width="stretch")

def render_viz_bed_need(df_inpatient, capacity):
    """Viz 3 — Besoin en lits supplémentaires = max(effectif - capacité nominale, 0) (F10)."""
    from src.business.capacity import calculate_bed_need

    need = df_inpatient["final_inpatient_census"].apply(lambda s: calculate_bed_need(s, capacity))
    fig = go.Figure(
        go.Bar(
            x=df_inpatient["date"],
            y=need,
            marker_color=["rgba(255,80,80,0.9)" if f else "rgba(255,80,80,0.5)" for f in df_inpatient["is_forecast"]],
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Lits manquants : <b>%{y}</b><extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Besoin en lits supplémentaires (capacité nominale : {capacity})",
        xaxis_title="Date", yaxis_title="Lits manquants",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", rangemode="tozero"),
        height=350,
    )
    st.plotly_chart(fig, width="stretch")
