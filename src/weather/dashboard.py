"""Dashboard de monitorizacion del pipeline ETL meteorologico."""

import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from weather.config import DEFAULT_CONFIG
from weather.load import load_parquet

matplotlib.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "DejaVu Sans"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid")


def load_all_data(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga todos los datos descargados de ambas fuentes."""
    df_om = load_parquet(data_dir, "open-meteo")
    df_nasa = load_parquet(data_dir, "nasa-power")
    return df_om, df_nasa


def plot_temperatura_por_ciudad(df: pd.DataFrame, output_dir: Path) -> None:
    """Grafica de temperatura maxima media anual por ciudad."""
    df["year"] = pd.to_datetime(df["date"]).dt.year
    resumen = df.groupby(["year", "location"])["temperature_max"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    for city in resumen["location"].unique():
        datos = resumen[resumen["location"] == city]
        ax.plot(datos["year"], datos["temperature_max"], marker="o", label=city)

    ax.set_title("Temperatura maxima media anual por ciudad (Open-Meteo)")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Temperatura maxima media (C)")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    out = output_dir / "temperatura_por_ciudad.png"
    fig.savefig(out, dpi=150)
    logger.info("Guardado: %s", out)
    plt.close()


def plot_precipitacion_anual(df: pd.DataFrame, output_dir: Path) -> None:
    """Grafica de precipitacion total anual por ciudad."""
    df["year"] = pd.to_datetime(df["date"]).dt.year
    resumen = df.groupby(["year", "location"])["precipitation"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=resumen, x="year", y="precipitation", hue="location", ax=ax)
    ax.set_title("Precipitacion total anual por ciudad (Open-Meteo)")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Precipitacion total (mm)")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    out = output_dir / "precipitacion_anual.png"
    fig.savefig(out, dpi=150)
    logger.info("Guardado: %s", out)
    plt.close()


def plot_radiacion_solar(df: pd.DataFrame, output_dir: Path) -> None:
    """Grafica de radiacion solar media mensual por ciudad (NASA POWER)."""
    df["month"] = pd.to_datetime(df["date"]).dt.month
    resumen = df.groupby(["month", "location"])["radiation"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    for city in resumen["location"].unique():
        datos = resumen[resumen["location"] == city]
        ax.plot(datos["month"], datos["radiation"], marker="o", label=city)

    ax.set_title("Radiacion solar media mensual por ciudad (NASA POWER)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Radiacion solar media (MJ/m2/dia)")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(
        [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
    )
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    out = output_dir / "radiacion_solar.png"
    fig.savefig(out, dpi=150)
    logger.info("Guardado: %s", out)
    plt.close()


def plot_pipeline_status(
    df_om: pd.DataFrame, df_nasa: pd.DataFrame, output_dir: Path
) -> None:
    """Grafica resumen del estado del pipeline."""
    ciudades = df_om["location"].nunique()
    registros_om = len(df_om)
    registros_nasa = len(df_nasa)
    invalidos = 0

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    axes[0].bar(
        ["Open-Meteo", "NASA POWER"],
        [registros_om, registros_nasa],
        color=["#2196F3", "#FF9800"],
    )
    axes[0].set_title("Registros descargados")
    axes[0].set_ylabel("Num. registros")

    axes[1].bar(["Ciudades"], [ciudades], color="#4CAF50")
    axes[1].set_title("Ciudades procesadas")
    axes[1].set_ylabel("Num. ciudades")
    axes[1].set_ylim(0, 10)

    axes[2].bar(
        ["Validos", "Invalidos"],
        [registros_om + registros_nasa, invalidos],
        color=["#4CAF50", "#F44336"],
    )
    axes[2].set_title("Calidad de datos")
    axes[2].set_ylabel("Num. registros")

    fig.suptitle(
        "Estado del pipeline ETL meteorologico", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    out = output_dir / "pipeline_status.png"
    fig.savefig(out, dpi=150)
    logger.info("Guardado: %s", out)
    plt.close()


def run(data_dir: str = DEFAULT_CONFIG.data_dir) -> None:
    """Genera todas las graficas del dashboard."""
    output_dir = Path("docs") / "img"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Cargando datos...")
    df_om, df_nasa = load_all_data(data_dir)

    if df_om.empty or df_nasa.empty:
        logger.error("No hay datos. Ejecuta primero el pipeline.")
        return

    logger.info("Generando graficas...")
    plot_pipeline_status(df_om, df_nasa, output_dir)
    plot_temperatura_por_ciudad(df_om, output_dir)
    plot_precipitacion_anual(df_om, output_dir)
    plot_radiacion_solar(df_nasa, output_dir)

    logger.info("Dashboard completado. Graficas en: %s", output_dir)


if __name__ == "__main__":
    run()
