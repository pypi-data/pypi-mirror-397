import pandas as pd
from datetime import date
from joblib import Parallel, delayed
from .helpers.ewma import ewma_with_anomalies_rolling_group
from .helpers.baseline import remove_outliers_iqr_and_sd
from .helpers.fb_prophet import detect_time_series_anomalies_fb_walkforward
from .helpers.preprocessing import create_full_calendar_and_interpolate
from .helpers.iso_forest import detect_time_series_anomalies_isoforest
from .helpers.DB_scan import detect_time_series_anomalies_dbscan

def process_group(model, name, group, group_columns, variable,
                  date_column, alpha, sigma, eval_periods, interval_width):

    if model == "baseline":
        return remove_outliers_iqr_and_sd(group, variable)

    if model == "EWMA":
        return ewma_with_anomalies_rolling_group(
            group, group_columns, variable, date_column, alpha, sigma, eval_periods
        )

    if model == "FB":
        return detect_time_series_anomalies_fb_walkforward(
            group, variable, date_column, eval_periods, interval_width
        )
    
    if model == 'ISF':
        return detect_time_series_anomalies_isoforest(
            group, variable, date_column, eval_periods
        )
    
    if model == 'DBSCAN':
        return detect_time_series_anomalies_dbscan(
            group, variable, date_column, eval_periods
        )


def run_pipeline(master_data, group_columns, variable,
                 date_column="week_start", freq="W-MON",
                 max_records=104, min_records=15,
                 contamination=0.03, random_state=42,
                 alpha=0.3, sigma=1.5, eval_periods=12,
                 interval_width=0.90):

    # preprocess calendar
    final_data = create_full_calendar_and_interpolate(
        master_data,
        group_columns,
        variable,
        date_column,
        freq
    )

    groups = list(final_data.groupby(group_columns))

  # Run in parallel (use all cores: n_jobs=-1)
        ## baseline
    results_baseline = Parallel(n_jobs=-1, verbose=0)(delayed(process_group)('baseline', name, group, group_columns, variable,date_column, alpha, sigma, eval_periods, interval_width) for name, group in groups)


            # Combine results back
    anamoly_key_channel_basepipeline= (
                pd.concat(results_baseline)
                  .sort_values(by=group_columns+[date_column])
            )
    print("anamoly_key_channel_basepipeline data frame created")
        
        ## FB

    results_fb = Parallel(n_jobs=-1, verbose=0)(delayed(process_group)('FB', name, group,group_columns, variable,date_column,
                                  alpha, sigma, eval_periods, interval_width) for name, group in groups)


            # Combine results back
    anamoly_key_channel_fb= (
                pd.concat(results_fb)
                  .sort_values(by=group_columns+[date_column])
            )

    print("anamoly_key_channel_fb data frame created")
    FB_cols = group_columns+[date_column]+["FB_forecast","FB_low","FB_high",
                                                            "FB_residual","FB_anomaly","is_FB_anomaly"]

    anamoly_key_channel_fb_final =  anamoly_key_channel_fb[FB_cols]
        
        ## EWMA
    results_EWMA = Parallel(n_jobs=-1, verbose=0)(
                delayed(process_group)('EWMA', name, group,group_columns, variable, date_column,
                                       alpha, sigma, eval_periods, interval_width) for name, group in groups)


                # Combine results back
    anamoly_key_channel_EWMA= (
                    pd.concat(results_EWMA)
                      .sort_values(by=group_columns+[date_column])
                )
    print("anamoly_key_channel_EWMA data frame created")
    print(anamoly_key_channel_EWMA.head())

        ## Isolation Forest
    results_ISF = Parallel(n_jobs=-1, verbose=0)(
    delayed(process_group)('ISF', name, group,group_columns, variable, date_column,
                                       alpha, sigma, eval_periods, interval_width) for name, group in groups)


        # Combine results back
    anamoly_key_channel_ISF= (
            pd.concat(results_ISF)
              .sort_values(by=group_columns+[date_column])
        )
    print(anamoly_key_channel_ISF.head())
    ISF_cols = group_columns+[date_column]+["isolation_forest_score", "is_IsoForest_anomaly"]
    anamoly_key_channel_ISF_final =  anamoly_key_channel_ISF[ISF_cols]
    
    print("anamoly_key_channel_ISF data frame created")
    
       ## DB Scan 
    results_DB = Parallel(n_jobs=-1, verbose=0)(
    delayed(process_group)('DBSCAN', name, group,group_columns, variable, date_column,
                                       alpha, sigma, eval_periods, interval_width) for name, group in groups)


        # Combine results back
    anamoly_key_channel_DB= (
            pd.concat(results_DB)
              .sort_values(by=group_columns+[date_column])
        )
        
    print(anamoly_key_channel_DB.head())
    DB_cols = group_columns+[date_column]+["dbscan_score", "is_DBSCAN_anomaly"]
    anamoly_key_channel_DB_final =  anamoly_key_channel_DB[DB_cols]
    
    print("anamoly_key_channel_DB data frame created")
    
        
    anomaly = anamoly_key_channel_basepipeline.merge(anamoly_key_channel_EWMA,  on= group_columns+[date_column], how='inner')
    anomaly = anomaly.merge(anamoly_key_channel_fb_final, on= group_columns+[date_column], how= 'inner')  
    anomaly = anomaly.merge(anamoly_key_channel_ISF_final, on= group_columns+[date_column], how= 'inner')  
    anomaly = anomaly.merge(anamoly_key_channel_DB_final, on= group_columns+[date_column], how= 'inner')  

        # ---- Unified anomaly flag (majority voting) ----
    anomaly_flags = [
            'is_IQR_anomaly', 'is_Percentile_anomaly',
            'is_MAD_anomaly', 
            'is_SD_anomaly', 
            'is_EWMA_anomaly', 'is_FB_anomaly','is_IsoForest_anomaly','is_DBSCAN_anomaly']

    anomaly['Anomaly_Votes'] = anomaly[anomaly_flags].sum(axis=1)
        # Majority rule: anomaly if flagged by at least half the methods
    anomaly['is_Anomaly'] = anomaly['Anomaly_Votes'] >= 4
        
        # Add refresh_date as the first column
    anomaly.insert(0, 'refresh_date', pd.to_datetime(date.today()))

    return anomaly
