"""Client HTTP de l'API de prédiction (utilisé par le dashboard).

Sur l'offre gratuite de Render, l'API est mise en veille après 15 minutes
d'inactivité et met environ une minute à se réveiller : le client réessaie donc
avec un délai croissant au lieu d'échouer au premier appel.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src import config

_RETRY = Retry(
    total=5,
    connect=5,
    read=2,
    backoff_factor=3,  # 0 s, 6 s, 12 s, 24 s... : couvre le réveil de l'API
    status_forcelist=(502, 503, 504),
    allowed_methods=frozenset({"GET", "POST"}),
    raise_on_status=False,
)

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        adapter = HTTPAdapter(max_retries=_RETRY)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session


def _headers() -> dict[str, str]:
    return {"X-API-Key": config.API_KEY} if config.API_KEY else {}


def _post(endpoint: str, payload: dict, label: str) -> list[float]:
    response = _get_session().post(
        f"{config.API_URL}{endpoint}",
        json=payload,
        headers=_headers(),
        timeout=config.API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    result = response.json()
    if "predictions" not in result:
        raise ValueError(f"The {label} API response does not contain 'predictions'.")
    return result["predictions"]


def call_readmission_api(readmissions: list[dict]) -> list[float]:
    """Appelle l'API de prédiction de réadmission."""
    return _post("/_readmission_predict", {"readmissions": readmissions}, "readmission")


def call_length_of_stay_api(lengths_of_stay: list[dict]) -> list[float]:
    """Appelle l'API de prédiction de durée de séjour."""
    return _post(
        "/_length_of_stay_predict", {"lengths_of_stay": lengths_of_stay}, "length of stay"
    )


def api_status() -> dict | None:
    """État de l'API (None si injoignable) — pour l'affichage dans le dashboard."""
    try:
        r = _get_session().get(f"{config.API_URL}/healthz", timeout=config.API_TIMEOUT_SECONDS)
        return r.json() if r.ok else None
    except requests.RequestException:
        return None
