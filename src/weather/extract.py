"""Módulo de extracción: clientes para Open-Meteo y NASA POWER."""

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

OPENMETEO_URL = "https://archive-api.open-meteo.com/v1/archive"
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def _get_with_retry(
    url: str, params: dict, max_retries: int = 3, delay: float = 2.0
) -> dict[str, Any]:
    """Realiza una petición GET con reintentos ante fallos transitorios."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(
                "Intento %d/%d fallido para %s: %s", attempt, max_retries, url, e
            )
            if attempt < max_retries:
                time.sleep(delay * attempt)
    raise RuntimeError(f"No se pudo conectar a {url} tras {max_retries} intentos")


def fetch_openmeteo(lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
    """Descarga datos históricos diarios de Open-Meteo para una ubicación.

    Args:
        lat: Latitud de la ubicación.
        lon: Longitud de la ubicación.
        start: Fecha de inicio en formato YYYY-MM-DD.
        end: Fecha de fin en formato YYYY-MM-DD.

    Returns:
        Diccionario con los datos JSON de la API.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "et0_fao_evapotranspiration",
        ],
        "timezone": "Europe/Madrid",
    }
    logger.info("Descargando Open-Meteo para (%.4f, %.4f)", lat, lon)
    return _get_with_retry(OPENMETEO_URL, params)


def fetch_nasa_power(lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
    """Descarga datos de radiación solar de NASA POWER para una ubicación.

    Args:
        lat: Latitud de la ubicación.
        lon: Longitud de la ubicación.
        start: Fecha de inicio en formato YYYYMMDD.
        end: Fecha de fin en formato YYYYMMDD.

    Returns:
        Diccionario con los datos JSON de la API.
    """
    start_fmt = start.replace("-", "")
    end_fmt = end.replace("-", "")
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,PRECTOTCORR",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_fmt,
        "end": end_fmt,
        "format": "JSON",
    }
    logger.info("Descargando NASA POWER para (%.4f, %.4f)", lat, lon)
    return _get_with_retry(NASA_POWER_URL, params)
