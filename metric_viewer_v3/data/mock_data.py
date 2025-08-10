from ..utils import DefaultParams, MockTimeSeriesParams
import numpy as np
import pandas as pd

def generate_timeseries(params: MockTimeSeriesParams, start_date=None):
    """
    Generate a time series as per the desired trend and fluctuation pattern.
    Returns a list of (date, value) tuples.
    """
    if params.random_seed is not None:
        np.random.seed(params.random_seed)
    if start_date is None:
        start_date = pd.to_datetime('today') - pd.Timedelta(days=params.length - 1)
    dates = [start_date + pd.Timedelta(days=i) for i in range(params.length)]
    values = np.full(params.length, params.base_value, dtype=float)

    # params.trend_type = 
    # params.fluctuation = 

    # Apply trend
    if params.trend_type == 'increasing':
        values += np.arange(params.length) * params.trend_strength
    elif params.trend_type == 'decreasing':
        values -= np.arange(params.length) * params.trend_strength
    elif params.trend_type == 'cyclical' and params.seasonality_period:
        values += params.seasonality_amplitude * np.sin(
            2 * np.pi * np.arange(params.length) / params.seasonality_period
        )
    elif params.trend_type == 'random':
        values += np.random.randn(params.length) * params.fluctuation_strength
    # 'stable' does nothing extra

    # Add seasonality if specified and not already applied
    if params.trend_type != 'cyclical' and params.seasonality_period:
        values += params.seasonality_amplitude * np.sin(
            2 * np.pi * np.arange(params.length) / params.seasonality_period
        )

    # Add fluctuation/noise
    if params.fluctuation == 'high':
        values += np.random.randn(params.length) * params.fluctuation_strength * 2
    elif params.fluctuation == 'low':
        values += np.random.randn(params.length) * params.fluctuation_strength
    # 'none' means no extra noise
    print(params.trend_type)
    print(params.fluctuation)
    return list(zip(dates, values))

if __name__ == "__main__":
    result = generate_timeseries()
    print(result[:10]) 
    