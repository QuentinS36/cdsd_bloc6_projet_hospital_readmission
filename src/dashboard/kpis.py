"""Module M6 — indicateurs de pilotage (saturation, sous-occupation, min/max/moyenne)."""

import streamlit as st

from src.business.capacity import (
    calculate_avg_occupancy_rate,
    calculate_capacity_days,
    calculate_capacity_thresholds,
)
from src.business.inpatient import calculate_kpi
from src.config import ALERT_DAY_THRESHOLD
from src.dashboard.alerts import render_alerts


def kpi_colors(
    overcapacity_days,
    undercapacity_days,
    avg_inpatient,
    lower_threshold,
    upper_threshold,
):
    """Couleurs des deltas. `avg_inpatient` et les seuils sont tous exprimés en lits."""
    overcapacity_color = "inverse" if overcapacity_days > ALERT_DAY_THRESHOLD else "normal"
    undercapacity_color = "inverse" if undercapacity_days > ALERT_DAY_THRESHOLD else "normal"
    out_of_range = avg_inpatient > upper_threshold or avg_inpatient < lower_threshold
    return overcapacity_color, undercapacity_color, "inverse" if out_of_range else "normal"


def render_kpi(df_inpatient, capacity, tolerance_range):
    lower_threshold, upper_threshold = calculate_capacity_thresholds(capacity, tolerance_range)
    avg_inpatient, max_inpatient, min_inpatient = calculate_kpi(df_inpatient)
    avg_occupancy_rate = calculate_avg_occupancy_rate(avg_inpatient, capacity)

    overcapacity_days, undercapacity_days = calculate_capacity_days(
        df_inpatient, lower_threshold, upper_threshold
    )
    overcapacity_color, undercapacity_color, alert_color = kpi_colors(
        overcapacity_days,
        undercapacity_days,
        avg_inpatient,
        lower_threshold,
        upper_threshold,
    )

    render_alerts(overcapacity_days, undercapacity_days, lower_threshold, upper_threshold)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(
        "Effectif moyen",
        avg_inpatient,
        delta=f"{avg_occupancy_rate:.0f}% capacité",
        delta_color=alert_color,
    )
    col2.metric(
        "Jours en saturation",
        value=int(overcapacity_days),
        delta="ALERTE" if overcapacity_days > ALERT_DAY_THRESHOLD else "RAS",
        delta_color=overcapacity_color,
        help=f"Nombre de jours où l'effectif dépasse {int(upper_threshold)} lits.",
    )
    col3.metric(
        "Jours en sous-occupation",
        value=int(undercapacity_days),
        delta="ALERTE" if undercapacity_days > ALERT_DAY_THRESHOLD else "RAS",
        delta_color=undercapacity_color,
        help=f"Nombre de jours où l'effectif est inférieur à {int(lower_threshold)} lits.",
    )
    col4.metric("Effectif maximum", int(max_inpatient))
    col5.metric("Effectif minimum", int(min_inpatient))
    st.markdown("---")
