import pytest
from datetime import date, timedelta
from utils import DefaultParams

def test_defaultparams_today_and_global_timeframe():
    params = DefaultParams()
    assert isinstance(params.today, date)
    assert isinstance(params.global_timeframe, tuple)
    assert params.global_timeframe[1] == params.today
    assert params.global_timeframe[0] == params.today - timedelta(days=89)

def test_defaultparams_latest_date_and_week_month():
    custom_date = date(2023, 12, 31)
    params = DefaultParams(latest_date=custom_date)
    assert params.latest_date == custom_date
    assert params.latest_week == custom_date.isocalendar()[:2]
    assert params.latest_month == (2023, 12)

def test_equal_span_timeframes():
    custom_date = date(2024, 3, 31)
    params = DefaultParams(latest_date=custom_date)
    tf = params.equal_span_timeframes
    assert tf['3_days'][1] == custom_date
    assert tf['3_days'][0] == custom_date - timedelta(days=2)
    assert tf['3_weeks'][0] == custom_date - timedelta(weeks=2)
    assert tf['3_weeks'][1] == custom_date
    # 3_months: first day 3 months ago to latest_date
    first_day_last_month = custom_date.replace(day=1) - timedelta(days=1)
    first_day_3_months_ago = first_day_last_month.replace(day=1)
    assert tf['3_months'][0] == first_day_3_months_ago
    assert tf['3_months'][1] == custom_date

def test_special_days_are_weekends():
    params = DefaultParams()
    for d in params.special_days:
        assert d.weekday() in (5, 6)  # Saturday or Sunday

def test_special_days_range():
    params = DefaultParams()
    start, end = params.global_timeframe
    assert all(start <= d <= end for d in params.special_days)