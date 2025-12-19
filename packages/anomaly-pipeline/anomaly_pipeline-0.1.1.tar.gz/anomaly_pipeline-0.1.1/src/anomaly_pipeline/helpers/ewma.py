import pandas as pd
import numpy as np

# # EWMA functions

def ewma_forecast(train, alpha):
    """Return last EWMA forecast value based on training data."""
    ewma = train.ewm(alpha=alpha, adjust=False).mean()
    return ewma.iloc[-1]


def ew_std(series, alpha):
    """
    Compute exponentially weighted standard deviation.
    Uses the same alpha as EWMA so recent points get more weight.

    Parameters
    ----------
    series : pandas Series of actual values
    alpha : float in (0,1)

    Returns
    -------
    float : exponentially weighted std deviation
    """
    # mean
    
    mean = series.mean()
    #print(mean)

    # Squared deviation from the mean
    squared_diff = (series - mean) ** 2
    
    #print(squared_diff)

    # EWMA of squared deviation → variance
    ewma_var = squared_diff.ewm(alpha=alpha, adjust=False).mean()
    #print(ewma_var)
    #print(ewma_var.iloc[-1])

    # Std = sqrt(var)
    return np.sqrt(ewma_var.iloc[-1])


def ewma_with_anomalies_rolling_group(group, group_columns, variable, date_column, alpha, sigma, eval_periods):
    
    """
    Rolling (expanding window) EWMA anomaly detection for a SINGLE GROUP ONLY.
    Expects `group` to already be filtered to one group.
    """

    group = group.sort_values(date_column).reset_index(drop=True)
    n = len(group)

    train_size = n - eval_periods  # rolling split

    # Build group key dictionary
    # group_columns can be list of multiple cols
    key_dict = {col: group[col].iloc[0] for col in group_columns}

    results = []

    for i in range(train_size, n):

        train = group.loc[:i-1, variable].astype(float)
        test_value = group.loc[i, variable]

        # --- EWMA + weighted STD ---
        ewma_train = train.ewm(alpha=alpha, adjust=False).mean()
        last_std = ew_std(train, alpha)
        forecast = ewma_forecast(train, alpha)

        upper_limit = forecast + sigma * last_std
        lower_limit = max(forecast - sigma * last_std, 0)

        anomaly = True if (test_value > upper_limit or test_value < lower_limit) else False

        # TRAIN part (added only once)
        if i == train_size:
            train_part = pd.concat([
                group.loc[:i-1, group_columns].reset_index(drop=True),
                pd.DataFrame({
                    date_column: group.loc[:i-1, date_column].values,
                    "alpha": alpha,
                    "sigma":sigma,
                    "EWMA_forecast": ewma_train.values,
                    "EWMA_STD": last_std,
                    "EWMA_high": np.nan,
                    "EWMA_low": np.nan,
                    "set": "TRAIN",
                    "is_EWMA_anomaly": pd.NA,
                })
            ], axis=1)

            results.append(train_part)

        # TEST row
        test_part = pd.DataFrame({
            **{col: [key_dict[col]] for col in key_dict},
            date_column: [group.loc[i, date_column]],
            "alpha": [alpha],
            "sigma":[sigma],
            "EWMA_forecast": [forecast],
            "EWMA_STD": [last_std],
            "EWMA_high": [upper_limit],
            "EWMA_low": [lower_limit],
            "set": ["TEST"],
            "is_EWMA_anomaly": [anomaly],
        })

        results.append(test_part)

    final_output = pd.concat(results, ignore_index=True)
    return final_output

