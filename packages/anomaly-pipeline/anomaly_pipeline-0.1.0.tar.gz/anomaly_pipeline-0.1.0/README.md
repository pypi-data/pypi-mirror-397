# qrf-anomaly-detection
Package to detect anomalies in time series data. The default parameters are defined for weekly time series data. If the time series is daily change the max_records, min_records and  frequncy  accordingly.

# For the developers
## bash code to update the package 
source fresh_anomaly_env/bin/activate # activate the virtual environemnet
conda deactivate # decativate the base
pip uninstall anomaly_pipeline # remove the old installation
pip install -e . # Install the updated package
### testing
python examples/run_example.py

Find the sample output file in output folder located under repo

# For users
The main function controls the entire parallel processing workflow. It's crucial to understand which arguments are mandatory data inputs and which are optional configuration parameters.

# Bash script to install package 

## 1. Create the environment using standard Python venv
python3 -m venv anomaly_env

## 2. Activate the environment
source anomaly_env/bin/activate

## 3. deactivate the base environment if any
conda deactivate
## 4. Install anomaly_pipiline package
pip install 'git+https://<token>@github.com/one-thd/qrf-anomaly-detection.git@jc_dev#egg=anomaly_pipeline'


# Use from anomaly_pipeline.main import main as run_anomaly_pipeline in the script


## Input_data: 

master_data: Mandatory,The input pandas DataFrame containing all time series data.

group_columns: Mandatory,"A list of column names defining the granularity of the time series". Ex: For pageviews we are analyzing at taxonomy and channel level/ so the froup columns will be ["Taxonomy", "Channel"]. For Ad request, we are doing the anomaly detection at taxonomy level. So, the group column will be ["Taxonomy"]

variable: Mandatory,The column name containing the time series value being analyzed. Ex: for pageviews it is 'page_views', for Ad_requests it is "ad_requests".

date_column,Optional,The column name containing the timestamp. Ex: for pageviews and ad requests "week_start"

freq: Optional,Pandas frequency string for calendar interpolation. Default : "W-MON"" (Weekly, starting Monday)"

max_records: Optional,Max records expected (used in pre-processing).Default: 104 (~ 2yaers worth of data)

min_records: Optional,Minimum records required for a group to be analyzed. Default : 15

contamination: Optional,Expected proportion of outliers for Isolation Forest.Default: 0.03 (3%)

random_state: Optional,Seed for reproducible results in stochastic models.Default : 42

alpha: Optional,EWMA smoothing factor (α). Default: 0.3

sigma: Optional,Number of standard deviations for EWMA bounds. Default : 1.5

eval_periods:Optional,"The length of the out-of-sample test period for walk-forward EWMA, DB-scan, FB and Isolation Forest (number of points/weeks)". Default: 12

interval_width: Optional,The uncertainty interval width for Prophet (FB model).,0.90 (90% confidence)

## Output columns: All the output values are at "group_columns" level. 

MIN_value
The minimum historical "variable" values 
________________________________________
MAX_value
The maximum historical "variable" values 
________________________________________
Percentile_low / Percentile_high
The 5th and 95th percentile  "variable" values
Used to detect unusually low or unusually high "variable" values.
________________________________________
Mean / SD (Standard Deviation)
The average "variable"and its standard deviation based on historical data.
________________________________________
SD1_low / SD1_high
One-standard-deviation control limits:
• SD1_low = mean − 1×SD (floored at 0)
• SD1_high = mean + 1×SD 
________________________________________
SD2_low / SD2_high
Two-standard-deviation control limits:
• SD2_low = mean − 2×SD (floored at 0)
• SD2_high = mean + 2×SD 
________________________________________
SD3_low / SD3_high
Three-standard-deviation control limits:
• SD3_low = mean − 3×SD (floored at 0)
• SD3_high = mean + 3×SD 
________________________________________
Median / MAD (Median Absolute Deviation)
Median of "variable" and the median of absolute deviations from the median.
Used for robust anomaly detection when data contains outliers.
________________________________________
MAD_low / MAD_high
MAD-based limits:
• MAD_low = median − 2.5 × MAD / 0.6745 (floored at 0)
• MAD_high = median + 2.5 × MAD / 0.6745 
________________________________________
Q1 / Q3 / IQR (Interquartile Range)
• Q1: 25th percentile
• Q3: 75th percentile
• IQR = Q3 − Q1
Used to detect unusually low or high "variable" values.
________________________________________
IQR_low / IQR_high
IQR-based limits:
• IQR_low = Q1 − 1.5 × IQR (floored at 0)
• IQR_high = Q3 + 1.5 × IQR 
________________________________________
Percentile_anomaly
Flags based on percentile limits:
• Low → value < Percentile_low
• High → value > Percentile_high
• None → within the range
________________________________________
SD_anomaly
Flags based on SD2 limits:
• Low → value < SD2_low
• High → value > SD2_high
• None → within the range
________________________________________
MAD_anomaly
Flags based on MAD limits:
• Low → value < MAD_low
• High → value > MAD_high
• None → within the range
________________________________________
IQR_anomaly
Flags based on IQR limits:
• Low → value < IQR_low
• High → value > IQR_high
• None → within the range
________________________________________
is_Percentile_anomaly / is_SD_anomaly / is_MAD_anomaly / is_IQR_anomaly
Boolean indicators stating whether each method classified the value as an anomaly (low or high).
________________________________________
Alpha
Smoothing factor used in EWMA. Higher values give more weight to recent observations.
________________________________________
EWMA_forecast
Expected value estimated using the EWMA model.
________________________________________
EWMA_STD
Rolling standard deviation of residuals around the EWMA forecast.
________________________________________
EWMA_high
Upper anomaly threshold (EWMA_forecast + sigma × EWMA_STD).
_____________________________________ 
EWMA_low
lower anomaly threshold (EWMA_forecast - sigma × EWMA_STD).
_____________________________________ 
Is_EWMA_anomaly
Boolean flag indicating whether the observed value falls outside the EWMA bounds.
________________________________________
FB_forecast
Expected value estimated using the EWMA model.
________________________________________
FB_low
Lower confidence interval of the Prophet forecast
________________________________________
FB_high
Upper confidence interval of the Prophet forecast.
_____________________________________ 
FB_residual
Difference between observed value and Prophet forecast.
_____________________________________ 
FB_anomaly
Raw anomaly indicator based on Prophet confidence bounds.
_____________________________________ 
Is_FB_anomaly
Boolean flag indicating a Prophet-detected anomaly.
______________________________________   
isolation_forest_score
Score from the Isolation Forest model indicating anomaly severity. Typical range: –0.5 to +0.5
• Higher scores = more normal
• Lower scores = more anomalous
________________________________________
is_IsoForest_anomaly
Boolean flag based on Isolation Forest model output:
• True → model predicts anomaly (prediction = –1)
• False → model predicts normal (prediction = 1)
______________________________________   
dbscan_score
Cluster label or distance score produced by DBSCAN (-1 indicates noise/anomaly).
________________________________________
is_DBSCAN_anomaly
Boolean flag indicating DBSCAN-detected anomaly.
________________________________________
Anomaly_Votes
Count of anomaly-detection methods that agree a point is anomalous.
Ranges from 0 to 8.
________________________________________
is_Anomaly
Final ensemble decision:
• True → value flagged anomalous by 4 or more methods
• False → fewer than 4 methods indicate anomaly


