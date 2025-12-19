from .pipeline import run_pipeline

def timeseries_anomaly_detection(master_data, group_columns, variable,
         date_column="week_start", freq="W-MON",
         max_records=104, min_records=15,
         contamination=0.03, random_state=42,
         alpha=0.3, sigma=1.5, eval_periods=12,
         interval_width=0.90):
    
    """
    Performs anomaly detection on grouped time-series data.

    This function identifies outliers within specific groups of data by analyzing 
    historical trends, applying statistical thresholds, and calculating 
    prediction intervals.

    Args:
        master_data (pd.DataFrame): The input dataset containing the time series.
        group_columns (list[str]): Columns used to partition the data (e.g., ['store_id', 'item_id']).
        variable (str): The target numerical column to analyze for anomalies.
        date_column (str): The column containing datetime information. Defaults to 'week_start'.
        freq (str): Frequency of the time series (Pandas offset alias). Defaults to 'W-MON'.
        max_records (int): Maximum historical records to consider for the model. Defaults to 104.
        min_records (int): Minimum records required to perform detection. Defaults to 15.
        contamination (float): Expected proportion of outliers in the data (0 to 0.5). Defaults to 0.03.
        random_state (int): Seed for reproducibility in stochastic models. Defaults to 42.
        alpha (float): Smoothing factor for trend calculations. Defaults to 0.3.
        sigma (float): Standard deviation multiplier for thresholding. Defaults to 1.5.
        eval_periods (int): Number of recent periods to evaluate for anomalies. Defaults to 12.
        interval_width (float): The confidence level for the prediction interval (0 to 1). Defaults to 0.9.

    Returns:
        pd.DataFrame: The original dataframe appended with anomaly flags and scores.
    """

    return run_pipeline(
        master_data=master_data,
        group_columns=group_columns,
        variable=variable,
        date_column=date_column,
        freq=freq,
        max_records=max_records,
        min_records=min_records,
        contamination=contamination,
        random_state=random_state,
        alpha=alpha,
        sigma=sigma,
        eval_periods=eval_periods,
        interval_width=interval_width
    )
    
    print("Anomaly pipeline successfully invoked via python -m!")

# change test_weeks to eval_periods: automate min_records based on eval_periods, 
# max_records = max_records + eval_records
# freq_daily: max_records based on frequency (for version 2) 104 for weekly
# split all the 5 functions and parametrize all the variables 
# change interval_width name to prophet_CI
# change FB_anomaly column to high low and none insted of -1, 1, 0

