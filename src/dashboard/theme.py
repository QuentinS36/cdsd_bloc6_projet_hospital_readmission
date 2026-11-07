"""Thème Plotly partagé par le dashboard (séparé de la config pour que l'API
n'ait pas besoin de plotly)."""

import plotly.graph_objects as go

TEMPLATE = go.layout.Template(
    layout=go.Layout(
        plot_bgcolor="rgba(0,0,0,0)",  # fond du plot bleu clair semi-transparent
        paper_bgcolor="rgba(0,0,0,0)",          # fond transparent du container
        font=dict(
            family="Arial",
            size=14,
            color="#0d3b66"  # texte bleu foncé
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0)",  # lignes de grille bleu très clair
            zeroline=False,
            tickfont=dict(color="#0d3b66")
        ),
        yaxis=dict(
            showgrid=False,
            gridcolor="rgba(29, 78, 138,0.2)",  # lignes de grille bleu très clair
            zeroline=False,
            tickfont=dict(color="#0d3b66")
        )
    )
)
SIZE = 500
COLOR_DISCRETE_SEQUENCE = ["#014E97", "#41B8D5", "#2994E5"]