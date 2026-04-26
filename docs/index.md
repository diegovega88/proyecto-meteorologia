# Análisis de Datos Meteorológicos

Proyecto final de Big Data centrado en el diseño e implementación de un pipeline ETL para datos meteorológicos en tiempo real.

## Descripción

El objetivo de este proyecto es construir un pipeline ETL capaz de ingerir datos meteorológicos desde múltiples fuentes, validarlos, transformarlos y almacenarlos de forma estructurada y eficiente.

## Fuente de datos

Se utilizarán las siguientes APIs abiertas:

- Open-Meteo
- NASA POWER

## Instalación

Ejecutar:

    uv sync --dev

## Ejecución de tests

Ejecutar:

    uv run pytest tests/ --cov=src --cov-report=term-missing -v

## Autor

Diego Vega
