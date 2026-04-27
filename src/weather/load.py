"""Módulo de carga: almacenamiento en formato Parquet particionado."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_parquet(df: pd.DataFrame, base_dir: str, source: str) -> list[Path]:
    """Guarda el DataFrame en Parquet particionado por año y ubicación.

    Args:
        df: DataFrame a guardar. Debe contener columnas 'date' y 'location'.
        base_dir: Directorio raíz donde se guardarán los datos.
        source: Nombre de la fuente (open-meteo, nasa-power).

    Returns:
        Lista de rutas de los archivos Parquet generados.
    """
    df = df.copy()
    df["year"] = df["date"].dt.year
    saved_paths: list[Path] = []

    for (year, location), group in df.groupby(["year", "location"]):
        out_dir = Path(base_dir) / source / f"year={year}" / f"location={location}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "data.parquet"
        group.drop(columns=["year"]).to_parquet(out_path, index=False)
        logger.info("Guardado: %s (%d filas)", out_path, len(group))
        saved_paths.append(out_path)

    return saved_paths


def load_parquet(base_dir: str, source: str) -> pd.DataFrame:
    """Carga todos los Parquet de una fuente en un único DataFrame.

    Args:
        base_dir: Directorio raíz de los datos.
        source: Nombre de la fuente (open-meteo, nasa-power).

    Returns:
        DataFrame combinado con todos los datos disponibles.
    """
    files = list(Path(base_dir).glob(f"{source}/**/data.parquet"))
    if not files:
        logger.warning("No se encontraron archivos en %s/%s", base_dir, source)
        return pd.DataFrame()

    dfs = [pd.read_parquet(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    logger.info("Cargados %d registros de %d archivos", len(combined), len(files))
    return combined
