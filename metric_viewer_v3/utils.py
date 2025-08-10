from datetime import date, timedelta, datetime
import calendar
import numpy as np

class DefaultParams:
    def __init__(self, latest_date=None):
        self.today = date.today()
        self.global_timeframe = (self.today - timedelta(days=89), self.today)  # last 90 days including today

        # latest_date: if not provided, use today
        self.latest_date = latest_date if latest_date else self.today

        # latest_week: ISO week (year, week number)
        self.latest_week = self.latest_date.isocalendar()[:2]

        # latest_month: (year, month)
        self.latest_month = (self.latest_date.year, self.latest_date.month)

        # equal_span_timeframes: example sets
        self.equal_span_timeframes = {
            '3_days': (self.latest_date - timedelta(days=2), self.latest_date),
            '3_weeks': (self.latest_date - timedelta(weeks=2), self.latest_date),
            '3_months': (
                (self.latest_date.replace(day=1) - timedelta(days=1)).replace(day=1),  # first day 3 months ago
                self.latest_date
            )
        }

        # special_days: all weekends in the last 90 days
        self.special_days = self._get_weekends_in_range(self.global_timeframe[0], self.global_timeframe[1])

    def _get_weekends_in_range(self, start_date, end_date):
        weekends = []
        current = start_date
        while current <= end_date:
            if current.weekday() >= 5:  # Saturday=5, Sunday=6
                weekends.append(current)
            current += timedelta(days=1)
        return weekends
    
class MockTimeSeriesParams:
    """
    Parameters for generating mock time series data with different trends and fluctuation patterns.
    """
    def __init__(
        self,
        length=90,
        trend_type='stable',  # 'stable', 'increasing', 'decreasing', 'cyclical', 'random'
        fluctuation='low',    # 'low', 'high', 'none'
        base_value=100,
        trend_strength=1.0,   # magnitude of increase/decrease per step
        fluctuation_strength=2.0,  # stddev for noise
        seasonality_period=None,   # e.g., 7 for weekly, 30 for monthly
        seasonality_amplitude=0.0, # amplitude of cyclical pattern
        random_seed=None
    ):
        self.length = length
        self.trend_type = trend_type
        self.fluctuation = fluctuation
        self.base_value = base_value
        self.trend_strength = trend_strength
        self.fluctuation_strength = fluctuation_strength
        self.seasonality_period = seasonality_period
        self.seasonality_amplitude = seasonality_amplitude
        self.random_seed = random_seed

    def describe(self):
        return {
            "length": self.length,
            "trend_type": self.trend_type,
            "fluctuation": self.fluctuation,
            "base_value": self.base_value,
            "trend_strength": self.trend_strength,
            "fluctuation_strength": self.fluctuation_strength,
            "seasonality_period": self.seasonality_period,
            "seasonality_amplitude": self.seasonality_amplitude,
            "random_seed": self.random_seed
        }
        
# Visually appealing and distinct color palette for graphing timeframes
TIMEFRAME_COLORS = {
    'today': '#1f77b4',         # blue
    'last_3_days': '#ff7f0e',   # orange
    'last_week': '#2ca02c',     # green
    'last_3_weeks': '#d62728',  # red
    'last_month': '#9467bd',    # purple
    'last_3_months': '#8c564b', # brown
    'weekends': '#e377c2',      # pink
    'global': '#7f7f7f',        # gray
}