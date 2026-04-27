"""Configuración central del pipeline ETL."""

from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Parámetros globales del pipeline."""

    locations: list[dict] = field(
        default_factory=lambda: [
            {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
            {"name": "Barcelona", "lat": 41.3888, "lon": 2.159},
            {"name": "Sevilla", "lat": 37.3891, "lon": -5.9845},
            {"name": "Valencia", "lat": 39.4699, "lon": -0.3763},
            {"name": "Bilbao", "lat": 43.263, "lon": -2.935},
            {"name": "Zaragoza", "lat": 41.6488, "lon": -0.8891},
            {"name": "Salamanca", "lat": 40.9701, "lon": -5.6635},
            {"name": "Tenerife", "lat": 28.2916, "lon": -16.6291},
        ]
    )

    start_date: str = "2020-01-01"
    end_date: str = "2024-12-31"
    data_dir: str = "data"
    max_retries: int = 3
    retry_delay: float = 2.0


DEFAULT_CONFIG = PipelineConfig()
