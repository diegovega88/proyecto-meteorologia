# Análisis de Datos Meteorológicos

> Proyecto final — Big Data · Grado en Matemáticas · UNIE Universidad

[![CI](https://github.com/diegovega88/proyecto-meteorologia/actions/workflows/ci.yml/badge.svg)](https://github.com/diegovega88/proyecto-meteorologia/actions/workflows/ci.yml)
[![Docs](https://github.com/diegovega88/proyecto-meteorologia/actions/workflows/docs.yml/badge.svg)](https://diegovega88.github.io/proyecto-meteorologia/)
[![Coverage](https://codecov.io/gh/diegovega88/proyecto-meteorologia/graph/badge.svg)](https://codecov.io/gh/diegovega88/proyecto-meteorologia)
[![Version](https://img.shields.io/github/v/release/diegovega88/proyecto-meteorologia)](https://github.com/diegovega88/proyecto-meteorologia/releases)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

---

## Description

Este proyecto implementa un pipeline ETL para la ingesta, validación, transformación y almacenamiento de datos meteorológicos procedentes de múltiples fuentes abiertas.

El objetivo es construir una arquitectura robusta que permita trabajar con datos reales, detectar inconsistencias y facilitar su posterior análisis.

Fuentes de datos utilizadas:

- Open-Meteo
- NASA POWER

## Documentation

Documentación completa disponible en:

https://diegovega88.github.io/proyecto-meteorologia/

## Installation

    git clone https://github.com/diegovega88/proyecto-meteorologia.git
    cd proyecto-meteorologia
    pip install uv
    uv sync --group dev

## Data Download

Los datos no se incluyen en el repositorio. Se obtienen mediante llamadas a APIs:

- Open-Meteo: https://open-meteo.com/
- NASA POWER: https://power.larc.nasa.gov/

Los scripts de ingesta se encargarán de descargar y almacenar los datos en la carpeta `data/`.

## Usage

    uv run pytest                          # ejecutar tests
    uv run pytest --cov=src -v             # tests con coverage
    uv run ruff check .                    # lint
    uv run ruff format .                   # formateo
    uv run mkdocs serve                    # documentación en local

## Project Structure

    proyecto-meteorologia/
    ├── .github/workflows/   # CI/CD pipelines
    ├── data/                # Datos no versionados
    ├── docs/                # Documentación MkDocs
    ├── src/weather/         # Código fuente
    ├── tests/               # Tests
    ├── mkdocs.yml
    ├── pyproject.toml
    └── README.md

## Author

Diego Vega · https://github.com/diegovega88

## Professor

Álvaro Diez · https://github.com/alvarodiez20

---

Big Data · 4º Grado en Matemáticas · UNIE Universidad · 2025–2026
