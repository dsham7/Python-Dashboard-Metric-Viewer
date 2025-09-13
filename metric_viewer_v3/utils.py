from datetime import date, timedelta, datetime
import calendar
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from math import sqrt


# params for timeframes
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

# params for timeseries    
class MockTimeSeriesParams:
    """
    Parameters for generating mock time series data with different trends and fluctuation patterns.
    """
    def __init__(
        self,
        length=90,
        trend_type='increasing',  # 'stable', 'increasing', 'decreasing', 'cyclical', 'random'
        fluctuation='low',    # 'low', 'high', 'none'
        base_value=np.random.randint(100,300),
        trend_strength=1.0,   # magnitude of increase/decrease per step
        fluctuation_strength=5,  # stddev for noise
        seasonality_period=15,   # e.g., 7 for weekly, 30 for monthly
        seasonality_amplitude=10,#*self.base_value, # amplitude of cyclical pattern
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
        
# Color palette for graphing timeframes
TIMEFRAME_COLORS = {
    'Today': '#1f77b4',         # blue
    'Last 3 Days': '#FFFDE7',   # light yellow
    'Last Week': '#2ca02c',     # green
    'Last 3 Weeks': '#F1F8E9',  # light lime
    'Last Month': '#9467bd',    # purple
    'Last 3 Months': '#8c564b', # brown
    'Weekends': '#e377c2',      # pink
    'Global': '#7f7f7f',        # gray
}

def stats_by_ser(df):
    periods = ['Last 3 Weeks','Last 3 Days','Weekends']
    is_weekday = df['Date'].dt.weekday < 5
    weekday_df = df.loc[is_weekday] # excludes weekends
    df[periods[2]] = ~is_weekday
    df[periods[1]] = df['Date'].apply(lambda x: 1 if x in weekday_df.iloc[-3:]['Date'].tolist() else 0)
    df[periods[0]] = df['Date'].apply(lambda x: 1 if x in weekday_df.iloc[-21:]['Date'].tolist() else 0)
    st_df = df.copy()
    df_p2 = df.loc[df[periods[2]]==True,['Date','Value','Timeseries']]
    df_p1 = df.loc[df[periods[1]]==1,['Date','Value','Timeseries']]
    df_p0 = df.loc[df[periods[0]]==1,['Date','Value','Timeseries']]
    result_df = pd.DataFrame()
    for df in [df_p2,df_p1,df_p0]:
        tmp = df.groupby('Timeseries')['Value'].mean()
        result_df = pd.concat([result_df,tmp],axis=1)
    result_df.columns = periods
    return result_df, st_df

# Function to process uploaded CSV data
def process_upload_data(upload_data):
    """
    Processes uploaded CSV data to ensure the first column is datetime and the second is float.
    Returns a tuple: (processed DataFrame or None, message or None)
    """
    try:
        df = pd.DataFrame(upload_data)
    except Exception as e:
        return None, f"Error in upload data transformation attempt: {e}"

    if df.shape[1] != 2:
        return None, "CSV must have at exactly two columns."

    # Attempt to convert first column to datetime
    col1 = df.columns[0]
    try:
        df[col1] = pd.to_datetime(df[col1])
    except Exception:
        return None, f"First column '{col1}' could not be converted to datetime."

    # Attempt to convert second column to float
    col2 = df.columns[1]
    try:
        df[col2] = pd.to_numeric(df[col2], errors='raise').astype(float)
    except Exception:
        return None, f"Second column '{col2}' could not be converted to float."

    try:
        df.columns = ['Date','Value']
    except:
        pass
    return df, None

def tf_label_to_tuple(df, timeframe_label):
    """
    Converts a timeframe label into a list of tuples representing 7-day periods within the timeframe.

    Args:
        df (pd.DataFrame): DataFrame with 'Date' and 'Value' columns.
        timeframe_label (str): Label indicating the timeframe (e.g., 'Last 28 days', 'Last 56 days').

    Returns:
        list: A list of tuples, where each tuple contains (label, start_date, end_date) for a 7-day period.
    """
    
    df['Date'] = pd.to_datetime(df['Date'])
    end_date = df['Date'].max()
    
    num_days = int(timeframe_label.split(' ')[1])
    start_date = end_date - timedelta(days=num_days - 1)  # Inclusive of start & end
    overall_tf = [(timeframe_label,start_date.date(),end_date.date())]
    time_periods = []
    current_start = start_date
    delta = 13 if num_days == 56 else 6
    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=delta), end_date)
        label = f'{current_start.strftime("%m-%d")} to {current_end.strftime("%m-%d")}'
        time_periods.append((label, current_start.date(), current_end.date()))  # Store dates, not datetimes
        current_start = current_end + timedelta(days=1)
    
    return time_periods, overall_tf


def Timeframe_corr(series_df, timeframes):
    """
    Compute pairwise correlation for slices of a time series DataFrame based on equal-span timeframes.

    Parameters:
    - series_df: pd.DataFrame with columns ['Date', 'Value']
    - timeframes: list of tuples -> (label, start_date, end_date)

    Returns:
    - pd.DataFrame containing the correlation matrix of valid timeframe slices
    """

    # Ensure 'Date' column is datetime
    series_df = series_df.copy()
    series_df['Date'] = pd.to_datetime(series_df['Date'])

    slices = {}

    valid_timeframes = None
    duration_list = []

    for label, start, end in timeframes:
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        mask = (series_df['Date'] >= start) & (series_df['Date'] <= end)
        values = series_df.loc[mask, 'Value'].values

        duration = (end - start).days + 1  # inclusive
        duration_list.append(duration)
        # skip non-uniform spans or missing days
        slices[label] = values

    same_durations = [duration_list.count(d) > 1 for d in duration_list]
    copy_of_slice_keys = list(slices.keys()).copy()
    for label, duration_boolean in zip(copy_of_slice_keys, same_durations):
        if not duration_boolean:
            del slices[label]
    if sum(same_durations) < 2:
        corr_matrix = pd.DataFrame(data=['No timeframes with same duration span (>1 day)'])
        return corr_matrix
    else:
        # Create a DataFrame from slices
        slice_df = pd.DataFrame(slices)
        corr_matrix = slice_df.corr()
        corr_matrix.index = slices.keys()
        corr_matrix.columns = slices.keys()

    return corr_matrix

def Series_corr(series_dict, timeframes, tf_label):
    tf_idx = [i for i, (lbl, _, _) in enumerate(timeframes) if lbl == tf_label]
    if not tf_idx:
        return pd.DataFrame()
    tf_idx = tf_idx[0]
    vals = []
    names = []
    min_len = None
    for name, df in series_dict.items():
        tf_start, tf_end = timeframes[tf_idx][1], timeframes[tf_idx][2]
        tf_start, tf_end = pd.to_datetime(tf_start),pd.to_datetime(tf_end)
        # Ensure Date column is datetime
        if not np.issubdtype(df['Date'].dtype, np.datetime64):
            df = df.copy()
            df['Date'] = pd.to_datetime(df['Date'])
        v = df[(df['Date'] >= tf_start) & (df['Date'] <= tf_end)]['Value'].values
        if len(v) == 0:
            continue
        if min_len is None or len(v) < min_len:
            min_len = len(v)
        vals.append(v)
        names.append(name)
    if len(vals) < 2 or min_len is None or min_len == 0:
        return pd.DataFrame(np.nan, index=names, columns=names)
    trimmed = [arr[:min_len] for arr in vals]
    data = np.column_stack(trimmed)
    valid_cols = [i for i in range(data.shape[1]) if np.std(data[:, i]) > 1e-8]
    if len(valid_cols) < 2:
        return pd.DataFrame(np.nan, index=[names[i] for i in valid_cols], columns=[names[i] for i in valid_cols])
    data = data[:, valid_cols]
    valid_names = [names[i] for i in valid_cols]
    corr = np.corrcoef(data, rowvar=False)
    return pd.DataFrame(corr, index=valid_names, columns=valid_names)

def forc(df, forecast_days=56):
    """
    Generates a SARIMAX forecast for the next 'forecast_days' days.

    Args:
        df (pd.DataFrame): DataFrame with 'Date' and 'Value' columns.
        forecast_days (int, optional): Number of days to forecast. Defaults to 56 (8 weeks).

    Returns:
        pd.DataFrame: DataFrame with 'Date' and 'Forecast' columns for the forecast period.
    """

    # Ensure the Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    df = df.reset_index(drop=True)
    df.set_index('Date',inplace=True)
    df = df.asfreq('D')

    train_data = df[:-forecast_days]  # Use the last 56 days as the test set
    test_data = df[-forecast_days:]
    model = SARIMAX(train_data['Value'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 15))
    model_fit = model.fit()
    # Make predictions
    predictions = model_fit.forecast(steps=56)
    rmse = sqrt(mean_squared_error(test_data['Value'], predictions))
    print(f"RMSE: {rmse} on test data (last 56 days)")
    # New prediction for future dates
    model = SARIMAX(df['Value'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 15))
    model_fit = model.fit()
    predictions = model_fit.forecast(steps=56)
    forecast_df = predictions.reset_index()
    forecast_df.columns = ['Date','Value']
    return forecast_df
