import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Anomaly category columns (optional, keep if you still want string labels)
def classify(val,lower,upper):
    if val < lower:
        return 'low'
    elif val > upper:
        return 'high'
    else:
        return 'none'

def remove_outliers_iqr_and_sd(group, variable,contamination=0.03, random_state=42):
    if len(group) < 10:
        # Return empty DataFrame to exclude this group entirely
        print(f"the {group[key].unique()} has {len(group)} records.Hence dropping from the analysis")
        return pd.DataFrame(columns=group.columns)
    # Quantile-based bounds
    min_value = group[variable].min()
    max_value = group[variable].max()
    Q1 = group[variable].quantile(0.25)
    Q3 = group[variable].quantile(0.75)
    median = group[variable].quantile(0.5)
    IQR = Q3 - Q1
    low_percentile = group[variable].quantile(0.05)
    high_percentile = group[variable].quantile(0.95)
    lower_q = max(Q1 - 1.5 * IQR,0)
    upper_q = Q3 + 1.5 * IQR
    
    group["MIN_value"]= min_value
    group["MAX_value"]= max_value
    group["Percentile_low"]=low_percentile
    group["Percentile_high"]=high_percentile
    
    # SD-based bounds
    mean = group[variable].mean()
    std = group[variable].std()
    
    lower_1sd = max(mean - 1*std, 0)
    upper_1sd = mean + 1*std
    group["Mean"]=mean
    group["SD"]=std
    group['SD1_low'] = lower_1sd
    group['SD1_high'] = upper_1sd

    lower_2sd = max(mean - 2*std,0)
    upper_2sd = mean + 2*std
    #group["mean"]=mean
    #group["std"]=std
    group['SD2_low'] = lower_2sd
    group['SD2_high'] = upper_2sd
    

    lower_3sd = max(mean - 3 * std,0)
    upper_3sd = mean + 3 * std
    group['SD3_low'] = lower_3sd
    group['SD3_high'] = upper_3sd
    
     
    # MAD-based bounds
    abs_dev = np.abs(group[variable] - median)
    mad = np.median(abs_dev)
    threshold_v1 = 2.5
    threshold_v2 = 2.5
    scale_factor = 0.6745

    if mad == 0:
        lower_mad_v1 = median
        upper_mad_v1= median
        lower_mad_v2 = median
        upper_mad_v2 = median
    else:
        margin_v1 = threshold_v1 * mad / scale_factor
        lower_mad_v1 = max(median - margin_v1,0)
        upper_mad_v1 = median + margin_v1
        margin_v2 = threshold_v2 * mad / scale_factor
        lower_mad_v2 = max(median - margin_v2,0)
        upper_mad_v2 = median + margin_v2
    
    group["Median"]=median
    group['MAD'] = mad
    #group['MAD2.5_low'] = lower_mad_v1
    #group['MAD2.5_high'] = upper_mad_v1
    group['MAD_low'] = lower_mad_v2
    group['MAD_high'] = upper_mad_v2
    
    
    group["Q1"]=Q1
    group["Q3"]= Q3
    group["IQR"]=IQR
    group['IQR_low'] = lower_q
    group['IQR_high'] = upper_q
    
    """
     # ---- Isolation Forest ----
    iso = IsolationForest(contamination=contamination, random_state=random_state)
    preds = iso.fit_predict(group[[variable]])
    scores = iso.decision_function(group[[variable]])
    
    group["IsolationForest_score"] = scores
    """
    
    group['Percentile_anomaly'] = group[variable].apply(lambda val: classify(val, low_percentile, high_percentile))
    group['SD_anomaly'] = group[variable].apply(lambda val: classify(val, lower_2sd, upper_2sd))
    group['MAD_anomaly'] = group[variable].apply(lambda val: classify(val, lower_mad_v2, upper_mad_v2))
    group['IQR_anomaly'] = group[variable].apply(lambda val: classify(val, lower_q, upper_q))
     
    # Boolean anomaly flags
    
    group['is_Percentile_anomaly'] = (group[variable] < low_percentile) | (group[variable] > high_percentile)
    group['is_SD_anomaly'] = (group[variable] < lower_2sd) | (group[variable] > upper_2sd)
    group['is_MAD_anomaly'] = (group[variable] < lower_mad_v2) | (group[variable] > upper_mad_v2)
    group['is_IQR_anomaly'] = (group[variable] < lower_q) | (group[variable] > upper_q)
    #group["is_IsolationForest_anomaly"] = preds == -1

    return group

