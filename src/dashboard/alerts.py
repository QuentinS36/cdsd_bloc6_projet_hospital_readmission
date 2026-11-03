"""Module M7 — alertes visuelles (F07 : alerte si > 1 jour en saturation)."""

import streamlit as st

from src.config import ALERT_DAY_THRESHOLD


def render_alerts(overcapacity_days, undercapacity_days, lower_threshold, upper_threshold):
    if overcapacity_days > ALERT_DAY_THRESHOLD:
        st.error(
            f"🚨 **Risque de saturation** : l'effectif dépasse {int(upper_threshold)} lits "
            f"sur {int(overcapacity_days)} jours de la période affichée."
        )
    if undercapacity_days > ALERT_DAY_THRESHOLD:
        st.warning(
            f"⚠️ **Sous-occupation** : l'effectif est inférieur à {int(lower_threshold)} lits "
            f"sur {int(undercapacity_days)} jours de la période affichée."
        )
    if (
        overcapacity_days <= ALERT_DAY_THRESHOLD
        and undercapacity_days <= ALERT_DAY_THRESHOLD
    ):
        st.success("✅ Aucune alerte : l'effectif reste dans la plage de tolérance.")
