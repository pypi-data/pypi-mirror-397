from .pipeline import run_pipeline

def timeseries_anomaly_detection(master_data, group_columns, variable,
         date_column="week_start", freq="W-MON",
         max_records=104, min_records=15,
         contamination=0.03, random_state=42,
         alpha=0.3, sigma=1.5, eval_periods=12,
         interval_width=0.90):

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

