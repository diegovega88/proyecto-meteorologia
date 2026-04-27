"""Tests unitarios para el módulo de transformación."""

import pandas as pd

from weather.transform import parse_nasa_power, parse_openmeteo, validate

SAMPLE_OPENMETEO = {
    "daily": {
        "time": ["2023-01-01", "2023-01-02"],
        "temperature_2m_max": [10.0, 12.0],
        "temperature_2m_min": [3.0, 4.0],
        "precipitation_sum": [0.0, 2.5],
        "windspeed_10m_max": [15.0, 20.0],
        "et0_fao_evapotranspiration": [1.2, 1.4],
    }
}


def test_parse_openmeteo_devuelve_filas_correctas():
    """El parser debe devolver tantas filas como fechas hay en la respuesta."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    assert len(df) == 2


def test_parse_openmeteo_columnas_existen():
    """El DataFrame debe tener las columnas esenciales."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    for col in [
        "date",
        "temperature_max",
        "temperature_min",
        "precipitation",
        "location",
    ]:
        assert col in df.columns


def test_parse_openmeteo_fecha_es_datetime():
    """La columna date debe ser de tipo datetime, no texto."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_parse_openmeteo_location_correcta():
    """El nombre de la ciudad debe quedar registrado en cada fila."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    assert (df["location"] == "Madrid").all()


def test_validate_temperatura_imposible_se_marca_invalida():
    """Una temperatura de 999°C debe marcarse como inválida."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    df.loc[0, "temperature_max"] = 999.0
    df_val = validate(df)
    assert not df_val["valid"].iloc[0]
    assert df_val["valid"].iloc[1]


def test_validate_datos_correctos_son_validos():
    """Datos dentro de rangos normales deben pasar la validación."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    df_val = validate(df)
    assert df_val["valid"].all()


def test_validate_elimina_duplicados():
    """Si hay filas duplicadas por fecha y ciudad, deben eliminarse."""
    df = parse_openmeteo(SAMPLE_OPENMETEO, "Madrid")
    df_dup = pd.concat([df, df], ignore_index=True)
    df_val = validate(df_dup)
    assert len(df_val) == 2


def test_nasa_power_convierte_999_a_nulo():
    """NASA POWER usa -999 para indicar dato ausente. Debe convertirse a NaN."""
    raw = {
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": {"20230101": -999.0},
                "T2M": {"20230101": 8.0},
                "PRECTOTCORR": {"20230101": 0.0},
            }
        }
    }
    df = parse_nasa_power(raw, "Madrid")
    assert pd.isna(df["radiation"].iloc[0])
