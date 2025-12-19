import pandas as pd
import numpy as np
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")


def detect_time_series_anomalies_fb_walkforward(
    group,
    variable,
    date_column,
    eval_periods,
    interval_width
):
    """
    Prophet walk-forward anomaly detection.
    Forecasts ONE point at a time and expands the training set iteratively.
    """

    group = group.sort_values(date_column).copy()
    group[date_column] = pd.to_datetime(group[date_column])

    # Boundary between rolling train and rolling forecast region
    cutoff_date = group[date_column].max() - pd.Timedelta(weeks=eval_periods)

    # Output columns
    group["FB_forecast"] = np.nan
    group["FB_low"] = np.nan
    group["FB_high"] = np.nan

    # -------------------------
    # 1. Initial Training Set
    # -------------------------
    train = group[group[date_column] <= cutoff_date].copy()
    test = group[group[date_column] > cutoff_date].copy()

    # -------------------------
    # 2. Walk-Forward Loop
    # -------------------------
    for i, row in test.iterrows():

        # Fit Prophet on current training window
        prophet_train = train.rename(columns={date_column: "ds", variable: "y"})

        try:
            model = Prophet(
                weekly_seasonality=True,
                yearly_seasonality=True,
                daily_seasonality=False,
                interval_width=interval_width
            )
            model.fit(prophet_train)

            # Forecast exactly ONE STEP (the next test point)
            future = pd.DataFrame({"ds": [row[date_column]]})
            fc = model.predict(future).iloc[0]

            # Save predictions
            group.loc[i, "FB_forecast"] = fc["yhat"]
            group.loc[i, "FB_low"] = max(fc["yhat_lower"],0)
            group.loc[i, "FB_high"] = fc["yhat_upper"]

        except Exception as e:
            print(f"Prophet failed for KEY={group['key'].iloc[0]} on date={row[date_column]}: {e}")
            # Baseline fallback
            group.loc[i, "FB_forecast"] = train[variable].iloc[-1]
            group.loc[i, "FB_low"] = max(train[variable].iloc[-1],0)
            group.loc[i, "FB_high"] = train[variable].iloc[-1]

        # Expand training window by appending the TRUE observed point
        new_train_row = row.to_frame().T
        train = pd.concat([train, new_train_row], ignore_index=True)

    # -------------------------
    # 3. Train region predictions = nan
    # -------------------------
    # Set the forecast values for the entire historical (training) period to NaN.
    group.loc[group[date_column] <= cutoff_date, "FB_forecast"] = np.nan
    group.loc[group[date_column] <= cutoff_date, ["FB_low", "FB_high"]] = np.nan

    # -------------------------
    # 4. Residuals
    # -------------------------
    group["FB_residual"] = group[variable] - group["FB_forecast"]
    
    # -------------------------
    # 5. Anomalies (only post-cutoff)
    # -------------------------
    group["FB_anomaly"] = np.nan
    mask = group[date_column] > cutoff_date

    group.loc[mask & (group[variable] > group["FB_high"]), "FB_anomaly"] = "high"
    group.loc[mask & (group[variable] < group["FB_low"]), "FB_anomaly"] = "low"

    # --- MODIFICATION START ---
    # Create the boolean anomaly flag (True/False) for the test region
    group["is_FB_anomaly"] = group["FB_anomaly"].notna()
    
    # Identify the training data indices
    train_mask = group[date_column] <= cutoff_date
    
    # Set 'is_FB_anomaly' to the string 'none' for the training data
    group.loc[train_mask, "FB_residual"] = np.nan
    group.loc[train_mask, "is_FB_anomaly"] = np.nan

    return group
