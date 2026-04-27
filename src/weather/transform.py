"""Módulo de transformación y validación de datos meteorológicos."""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

VALID_RANGES = {
    "temperature_max": (-40.0, 55.0),
    "temperature_min": (-40.0, 55.0),
    "precipitation": (0.0, 500.0),
    "windspeed": (0.0, 250.0),
    "radiation": (0.0, 400.0),
}


def parse_openmeteo(raw: dict[str, Any], location_name: str) -> pd.DataFrame:
    """Convierte la respuesta JSON de Open-Meteo en un DataFrame limpio.

    Args:
        raw: Diccionario JSON devuelto por la API de Open-Meteo.
        location_name: Nombre de la ubicación para etiquetar los datos.

    Returns:
        DataFrame con columnas estandarizadas y tipos correctos.
    """
    daily = raw.get("daily", {})
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily.get("time", [])),
            "temperature_max": daily.get("temperature_2m_max"),
            "temperature_min": daily.get("temperature_2m_min"),
            "precipitation": daily.get("precipitation_sum"),
            "windspeed": daily.get("windspeed_10m_max"),
            "evapotranspiration": daily.get("et0_fao_evapotranspiration"),
            "source": "open-meteo",
            "location": location_name,
        }
    )
    return df


def parse_nasa_power(raw: dict[str, Any], location_name: str) -> pd.DataFrame:
    """Convierte la respuesta JSON de NASA POWER en un DataFrame limpio.

    Args:
        raw: Diccionario JSON devuelto por NASA POWER.
        location_name: Nombre de la ubicación para etiquetar los datos.

    Returns:
        DataFrame con columnas estandarizadas y tipos correctos.
    """
    params = raw.get("properties", {}).get("parameter", {})
    radiation = params.get("ALLSKY_SFC_SW_DWN", {})
    temp = params.get("T2M", {})
    precip = params.get("PRECTOTCORR", {})

    dates = sorted(radiation.keys())
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(dates, format="%Y%m%d"),
            "radiation": [radiation[d] for d in dates],
            "temperature_mean": [temp.get(d) for d in dates],
            "precipitation": [precip.get(d) for d in dates],
            "source": "nasa-power",
            "location": location_name,
        }
    )
    df.replace(-999.0, pd.NA, inplace=True)
    return df


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica validaciones de calidad sobre el DataFrame.

    Args:
        df: DataFrame a validar.

    Returns:
        DataFrame con columna 'valid' indicando si cada fila pasa el control.
    """
    df = df.copy()
    df["valid"] = True

    range_map = {
        "temperature_max": VALID_RANGES["temperature_max"],
        "temperature_min": VALID_RANGES["temperature_min"],
        "precipitation": VALID_RANGES["precipitation"],
        "windspeed": VALID_RANGES["windspeed"],
        "radiation": VALID_RANGES["radiation"],
    }

    for col, (low, high) in range_map.items():
        if col in df.columns:
            mask = df[col].notna() & (~df[col].between(low, high))
            invalid_count = mask.sum()
            if invalid_count > 0:
                logger.warning(
                    "Columna '%s': %d valores fuera de rango", col, invalid_count
                )
            df.loc[mask, "valid"] = False

    dup_mask = df.duplicated(subset=["date", "location"], keep="first")
    if dup_mask.sum() > 0:
        logger.warning("Eliminados %d registros duplicados", dup_mask.sum())
    df = df[~dup_mask]

    return df
