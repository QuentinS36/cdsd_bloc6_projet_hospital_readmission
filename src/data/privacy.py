"""Pseudonymisation (RGPD, art. 5 et 9 — données de santé).

Les identifiants patients ne sont jamais affichés en clair dans le dashboard :
ils sont remplacés par une empreinte HMAC-SHA256 tronquée. Sans sel défini par
l'environnement, le sel est aléatoire pour la durée du processus (les pseudonymes
restent cohérents dans une session mais ne sont pas rejouables ensuite).
"""

import hashlib
import hmac
import secrets

import pandas as pd

from src import config

_PROCESS_SALT = secrets.token_hex(16)


def _salt() -> bytes:
    return (config.PSEUDONYMIZATION_SALT or _PROCESS_SALT).encode()


def pseudonymize(values: pd.Series, length: int = 10) -> pd.Series:
    """Remplace chaque identifiant par une empreinte tronquée (déterministe pour un sel donné)."""
    salt = _salt()
    return values.astype(str).map(
        lambda v: hmac.new(salt, v.encode(), hashlib.sha256).hexdigest()[:length]
    )
