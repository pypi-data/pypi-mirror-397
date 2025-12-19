import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.stattools import acf

def get_dynamic_lags(series: pd.Series) -> list:
    
    n = len(series)
    
    # Determine Max Lags (Max is min(50% of data, a hard cap of 60))
    nlags = min(int(n * 0.5), 60)
    
    if nlags < 5:
        return [1, 2, 3]

    # Calculate ACF and Confidence Intervals, get the 10 most-significant lags
    autocorrelations, confint = acf(series.dropna(), nlags=nlags, alpha=0.25, fft=True)
    autocorr_values = autocorrelations[1:]
    conf_limit = confint[1:, 1] - autocorr_values
    is_significant = np.abs(autocorr_values) > conf_limit
    significant_autocorr = autocorr_values[is_significant]
    significant_lags_indices = np.where(is_significant)[0] + 1
    ranked_indices = np.argsort(np.abs(significant_autocorr))[::-1]
    top_lags_indices = ranked_indices[:10]
    top_lags = significant_lags_indices[top_lags_indices].tolist()
    base_lags = [1, 2, 3]
    dynamic_lags = sorted(list(set(base_lags + top_lags)))[:10]
    
    return dynamic_lags

def detect_time_series_anomalies_isoforest(
    group,
    variable,
    date_column,
    eval_periods,
    ):
    
    group[date_column] = pd.to_datetime(group[date_column])
    group = group.copy().sort_values(date_column).reset_index(drop=True)
    
    '''
    Iterate over each of the evaluation periods, fitting the model to all the data before the evaluation period
    and then getting the predicted anomaly score for the given evaluation period
    '''
    try:
        test_anom = []

        for t in list(range(eval_periods - 1, -1, -1)):

            try:

                # Boundary between rolling train and rolling forecast region
                cutoff_date = group[date_column].max() - pd.Timedelta(weeks=t)

                # Get train set to determine lags
                model_group = group.copy()
                train = model_group[model_group[date_column] <= cutoff_date].copy()
                lags = get_dynamic_lags(train[variable])

                # Create lag features on the entire model_group DF
                for lag in lags:
                    model_group[f'lag{lag}'] = model_group[variable].shift(lag)

                # Get rolling stats features for the entire model_group DF
                rolling_stats_features = []    
                for w in [int(np.ceil(max(lags)/4)), int(np.ceil(max(lags)/2)), int(max(lags))]:
                    if w >= 3:
                        rolling_stats_features.append('roll_mean' + str(w))
                        rolling_stats_features.append('roll_std' + str(w))
                        model_group['roll_mean' + str(w)] = model_group[variable].shift(1).rolling(w).mean()
                        model_group['roll_std' + str(w)] = model_group[variable].shift(1).rolling(w).std()

                # Get trend feature
                model_group['trend'] = group.index

                # Drop records with NAs
                model_group = model_group.copy().dropna()

                # Split into train and test (train and test now both have all the features
                train = model_group[model_group[date_column] <= cutoff_date].copy()
                test = model_group[model_group[date_column] == cutoff_date].copy()

                # Identify all model features (lags, rolling stats, trend, and the variable itself)
                features = [f'lag{i}' for i in lags] + rolling_stats_features +  ['trend'] + [variable]

                # Create and fit the model
                iso_forest_model = IsolationForest(
                    n_estimators=200,
                    contamination=0.01,
                    random_state=42
                    )
                iso_forest_model.fit(train[features])

                train['isolation_forest_score'] = iso_forest_model.decision_function(train[features])
                anomaly_threshold = min(0,
                    train[train['isolation_forest_score'] > 0]['isolation_forest_score'].mean() - 3 * train[train['isolation_forest_score'] > 0]['isolation_forest_score'].std())
                test['isolation_forest_score'] = iso_forest_model.decision_function(test[features])
                test['contamination_anomaly'] = iso_forest_model.predict(test[features])  # -1 = anomaly, 1 = normal
                test['anomaly_threshold'] = anomaly_threshold
                test['threshold_anomaly'] = np.where(test['isolation_forest_score'] < anomaly_threshold, -1, 1)

                test['is_IsoForest_anomaly'] = np.where((test['contamination_anomaly'] == -1) & (test['threshold_anomaly'] == -1), True, False)
                test = test[[variable, date_column, 'isolation_forest_score', 'is_IsoForest_anomaly']]
                test_anom.append(test)
            except:
                pass
        try:
            test_anom = pd.concat(test_anom)
            group = group.merge(test_anom[[variable, date_column, 'isolation_forest_score', 'is_IsoForest_anomaly']], on=[variable, date_column], how='left')
        except:
            print("Error in Isolation Forest process")
            group["isolation_forest_score"] = np.nan
            group["is_IsoForest_anomaly"] = np.nan
    
    except:
        group["isolation_forest_score"] = np.nan
        group["is_IsoForest_anomaly"] = np.nan
        # Get string or object dtype columns from group that would identify the group
        group_id = key_series.select_dtypes(include=['object', 'string']).columns.tolist()
        group_id = " ".join(key_series[group_id].reset_index(drop=True).iloc[0].to_list())
        print(f'Isolation Forest Anomaly Detection failed for {group_id}')
    
    return group
