"""Pipeline ETL principal: orquesta extract, transform y load."""

import logging
import time
from dataclasses import dataclass, field

from weather.config import DEFAULT_CONFIG, PipelineConfig
from weather.extract import fetch_nasa_power, fetch_openmeteo
from weather.load import save_parquet
from weather.transform import parse_nasa_power, parse_openmeteo, validate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineReport:
    """Resumen de ejecución del pipeline."""

    locations_processed: int = 0
    records_openmeteo: int = 0
    records_nasa: int = 0
    invalid_records: int = 0
    errors: list[str] = field(default_factory=list)


def run(config: PipelineConfig = DEFAULT_CONFIG) -> PipelineReport:
    """Ejecuta el pipeline ETL completo.

    Args:
        config: Configuración del pipeline. Usa DEFAULT_CONFIG si no se especifica.

    Returns:
        PipelineReport con el resumen de la ejecución.
    """
    report = PipelineReport()
    start_time = time.time()
    logger.info("=== Iniciando pipeline ETL meteorológico ===")
    logger.info(
        "Ubicaciones: %d | Periodo: %s → %s",
        len(config.locations),
        config.start_date,
        config.end_date,
    )

    for loc in config.locations:
        name = loc["name"]
        lat = loc["lat"]
        lon = loc["lon"]
        logger.info("--- Procesando: %s ---", name)

        # --- Open-Meteo ---
        try:
            raw_om = fetch_openmeteo(lat, lon, config.start_date, config.end_date)
            df_om = parse_openmeteo(raw_om, name)
            df_om = validate(df_om)
            report.invalid_records += (~df_om["valid"]).sum()
            df_om_valid = df_om[df_om["valid"]].drop(columns=["valid"])
            save_parquet(df_om_valid, config.data_dir, "open-meteo")
            report.records_openmeteo += len(df_om_valid)
        except Exception as e:
            msg = f"Error Open-Meteo ({name}): {e}"
            logger.error(msg)
            report.errors.append(msg)

        # --- NASA POWER ---
        try:
            raw_nasa = fetch_nasa_power(lat, lon, config.start_date, config.end_date)
            df_nasa = parse_nasa_power(raw_nasa, name)
            df_nasa = validate(df_nasa)
            report.invalid_records += (~df_nasa["valid"]).sum()
            df_nasa_valid = df_nasa[df_nasa["valid"]].drop(columns=["valid"])
            save_parquet(df_nasa_valid, config.data_dir, "nasa-power")
            report.records_nasa += len(df_nasa_valid)
        except Exception as e:
            msg = f"Error NASA POWER ({name}): {e}"
            logger.error(msg)
            report.errors.append(msg)

        report.locations_processed += 1

    elapsed = time.time() - start_time
    logger.info("=== Pipeline completado en %.1fs ===", elapsed)
    logger.info(
        "Registros Open-Meteo: %d | NASA POWER: %d | Inválidos: %d | Errores: %d",
        report.records_openmeteo,
        report.records_nasa,
        report.invalid_records,
        len(report.errors),
    )

    return report


if __name__ == "__main__":
    run()
