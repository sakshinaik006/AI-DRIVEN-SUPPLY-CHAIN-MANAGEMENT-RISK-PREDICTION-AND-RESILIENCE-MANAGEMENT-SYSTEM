"""Forecasting training entrypoint.

Routes directly to the validated chronological forecasting pipeline in src/forecast/run_forecasts.py.
Eliminates random Poisson simulation, proxy multipliers, and exponential noise.
"""
from src.forecast.run_forecasts import generate_forecasts


def build_forecast_scores():
    return generate_forecasts()


if __name__ == "__main__":
    build_forecast_scores()