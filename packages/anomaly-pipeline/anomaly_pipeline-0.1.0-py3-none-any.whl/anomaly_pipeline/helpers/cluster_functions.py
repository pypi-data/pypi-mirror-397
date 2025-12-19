import pandas as pd
import numpy as np
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
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
                model_group = group.copy()[[date_column, variable]]
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
                test['isolation_forest_anomaly_threshold'] = anomaly_threshold
                test['threshold_anomaly'] = np.where(test['isolation_forest_score'] < anomaly_threshold, -1, 1)

                test['is_IsolationForest_anomaly'] = np.where((test['contamination_anomaly'] == -1) & (test['threshold_anomaly'] == -1), True, False)
                test = test[[variable, date_column, 'isolation_forest_anomaly_threshold', 'isolation_forest_score', 'is_IsolationForest_anomaly']]
                test_anom.append(test)
            except:
                pass
        try:
            test_anom = pd.concat(test_anom)
            group = group.merge(test_anom[[variable, date_column, 'isolation_forest_anomaly_threshold', 'isolation_forest_score', 'is_IsolationForest_anomaly']],
                                on=[variable, date_column], how='left')
        except:
            print("Error in Isolation Forest process")
            group["isolation_forest_anomaly_threshold"] = np.nan
            group["isolation_forest_score"] = np.nan
            group["is_IsolationForest_anomaly"] = np.nan
    
    except:
        group["isolation_forest_anomaly_threshold"] = np.nan
        group["isolation_forest_score"] = np.nan
        group["is_IsolationForest_anomaly"] = np.nan
        # Get string or object dtype columns from group that would identify the group
        group_id = key_series.select_dtypes(include=['object', 'string']).columns.tolist()
        group_id = " ".join(key_series[group_id].reset_index(drop=True).iloc[0].to_list())
        print(f'Isolation Forest Anomaly Detection failed for {group_id}')
    
    return group


def find_optimal_epsilon(X_scaled: np.ndarray, k: int) -> float:
    """
    Finds the optimal epsilon by calculating the distance to the k-th nearest neighbor
    and taking a high percentile (90-95th) of those distances as the cutoff.
    This serves as a programmatic proxy for the 'elbow' method in a rolling window.
    """
    if len(X_scaled) < k:
        return 1.0 # Fallback 

    # Find the distance to the k-th (min_samples) neighbor for every point
    # n_neighbors is k+1 because the first distance is 0 (to itself)
    neigh = NearestNeighbors(n_neighbors=k + 1) 
    neigh.fit(X_scaled)
    
    # distances matrix: [n_samples, k+1]
    distances, indices = neigh.kneighbors(X_scaled)
    
    # We are interested in the distance to the k-th neighbor (index k)
    # This k-distance is the required radius for a point to be a core point's neighbor.
    k_distances = distances[:, k] 
    
    # The elbow is hard to find programmatically. A robust proxy for the density
    # threshold is to take a high percentile (e.g., 95th) of the k-distances. 
    # This sets epsilon such that 95% of your *training* points would be considered
    # part of a cluster's neighborhood.
    optimal_eps = np.percentile(k_distances, 95) 
    
    # Ensure a minimum value if data is extremely sparse
    return max(optimal_eps, 0.1)


def detect_time_series_anomalies_dbscan(
    group,
    variable,
    date_column,
    eval_periods,
    ):
    
    group[date_column] = pd.to_datetime(group[date_column])
    group = group.copy().sort_values(date_column).reset_index(drop=True)
    
    # --- Default DBSCAN Parameters ---
    # These parameters often need tuning, but these are reasonable starting points:
    DEFAULT_EPS = 0.5 # Neighborhood radius (critical parameter)
    
    try:
        test_anom = []

        for t in list(range(eval_periods - 1, -1, -1)):

            try:
                # Boundary between rolling train and rolling forecast region
                cutoff_date = group[date_column].max() - pd.Timedelta(weeks=t)

                # Get train set to determine lags
                model_group = group.copy()[[date_column, variable]]
                train = model_group[model_group[date_column] <= cutoff_date].copy()
                lags = get_dynamic_lags(train[variable])

                # Create lag features and rolling stats for the entire DF
                rolling_stats_features = []
                for lag in lags:
                    model_group[f'lag{lag}'] = model_group[variable].shift(lag)

                for w in [int(np.ceil(max(lags)/4)), int(np.ceil(max(lags)/2)), int(max(lags))]:
                    if w >= 3:
                        rolling_stats_features.extend([f'roll_mean_{w}', f'roll_std_{w}'])
                        model_group[f'roll_mean_{w}'] = model_group[variable].shift(1).rolling(w).mean()
                        model_group[f'roll_std_{w}'] = model_group[variable].shift(1).rolling(w).std()

                model_group['trend'] = group.index
                model_group = model_group.copy().dropna()

                # Split into train and test
                train = model_group[model_group[date_column] <= cutoff_date].copy()
                test = model_group[model_group[date_column] == cutoff_date].copy()

                # Identify all model features (lags, rolling stats, trend, and the variable itself)
                features = [f'lag{i}' for i in lags] + rolling_stats_features + ['trend'] + [variable]

                # Fit the scaler ONLY on the training data to avoid data leakage
                scaler = StandardScaler()

                # Fit the scaler on the train data features
                scaler.fit(train[features])

                # Transform both train and test sets
                train_scaled = scaler.transform(train[features])
                test_scaled = scaler.transform(test[features])

                # Determine min_samples based on feature space dimension
                min_samples = max(2 * len(features), 3)

                # Find optimal epsilon
                calculated_eps = find_optimal_epsilon(train_scaled, k=min_samples)

                # --- DBSCAN MODEL ---
                dbscan_model = DBSCAN(
                    eps=calculated_eps, 
                    min_samples=min_samples,
                    n_jobs=-1
                )

                # Fit DBSCAN on the scaled training data
                dbscan_model.fit(train_scaled)

                # Since DBSCAN doesn't have a direct predict() method for new data points,
                # the simplest (and common) proxy is to treat the test point as unassigned noise,
                # which requires complex distance logic.

                neigh = NearestNeighbors(n_neighbors=min_samples)
                neigh.fit(train_scaled)

                # Find the distance of the test point to its nearest neighbors in the train set
                distances, indices = neigh.kneighbors(test_scaled)

                # Anomaly check: If the distance to the min_samples-th neighbor is > eps, it's noise.
                # Use the distance to the k-th neighbor (index min_samples-1)
                k_distance = distances[:, min_samples - 1] 

                # Flag as anomaly if the k-distance is greater than the trained eps threshold
                test['dbscan_anomaly_threshold'] = 0
                test['DBSCAN_score'] = k_distance - calculated_eps
                test['is_DBSCAN_anomaly'] = np.where(k_distance > calculated_eps, True, False)

                test = test[[variable, date_column, 'dbscan_anomaly_threshold', 'DBSCAN_score', 'is_DBSCAN_anomaly']]
                test_anom.append(test)

            except Exception as e:
                print(f"Error in iteration {t}: {e}")
                pass

        try:
            test_anom = pd.concat(test_anom)
            group = group.merge(test_anom[[variable, date_column, 'DBSCAN_score', 'is_DBSCAN_anomaly']], on=[variable, date_column], how='left')
        except:
            print("Error in DBSCAN process")
            group['dbscan_anomaly_threshold'] = np.nan
            group['DBSCAN_score'] = np.nan
            group["is_DBSCAN_anomaly"] = np.nan

    except Exception as e:
        # Fallback error handling
        # Replace key_series with group for robustness if key_series is not defined
        try:
             group_id_cols = group.select_dtypes(include=['object', 'string']).columns.tolist()
             group_id = " ".join(group[group_id_cols].reset_index(drop=True).iloc[0].astype(str).to_list())
        except:
             group_id = "Unknown Group ID"
        print(f'DBSCAN Anomaly Detection failed for {group_id}. Error: {e}')
        group['dbscan_anomaly_threshold'] = np.nan
        group['DBSCAN_score'] = np.nan
        group["is_DBSCAN_anomaly"] = np.nan
        
    return group
