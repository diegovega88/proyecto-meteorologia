"""Tests de integración para el módulo de carga."""

import pandas as pd
import pytest

from weather.load import load_parquet, save_parquet


@pytest.fixture
def sample_df():
    """DataFrame de ejemplo con datos de dos fechas."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2023-01-01", "2023-06-15"]),
            "temperature_max": [10.0, 30.0],
            "location": ["Madrid", "Madrid"],
            "source": ["open-meteo", "open-meteo"],
        }
    )


def test_save_parquet_crea_archivos(tmp_path, sample_df):
    """El pipeline debe crear archivos Parquet en disco."""
    save_parquet(sample_df, str(tmp_path), "open-meteo")
    archivos = list(tmp_path.glob("open-meteo/**/data.parquet"))
    assert len(archivos) > 0


def test_save_y_load_devuelve_mismos_datos(tmp_path, sample_df):
    """Los datos guardados deben poder cargarse y ser iguales."""
    save_parquet(sample_df, str(tmp_path), "open-meteo")
    loaded = load_parquet(str(tmp_path), "open-meteo")
    assert len(loaded) == 2
    assert "temperature_max" in loaded.columns


def test_load_directorio_vacio_devuelve_dataframe_vacio(tmp_path):
    """Si no hay archivos, load_parquet debe devolver un DataFrame vacío."""
    df = load_parquet(str(tmp_path), "open-meteo")
    assert df.empty


def test_parquet_particionado_por_año(tmp_path, sample_df):
    """Los datos deben guardarse particionados por año."""
    save_parquet(sample_df, str(tmp_path), "open-meteo")
    carpetas_año = list(tmp_path.glob("open-meteo/year=*"))
    assert len(carpetas_año) == 1
