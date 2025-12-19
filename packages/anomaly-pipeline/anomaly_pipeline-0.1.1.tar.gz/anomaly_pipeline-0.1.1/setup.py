from setuptools import setup, find_packages

setup(
    name="anomaly_pipeline",
    version="0.1.1",
    package_dir={"": "src"},
    # STOP using find_packages(). List them manually:
    packages=["anomaly_pipeline", "anomaly_pipeline.helpers"],
    install_requires=[
        "pandas",
        "numpy<2",  # important to avoid _ARRAY_API errors
        "joblib",
        "prophet",
        "scikit-learn",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "statsmodels",
        "plotly",
        "pandas-gbq", 
        "gcsfs",
    ],
    
    # 👇 This is the crucial part you were missing!
    entry_points={
        'console_scripts': [
            # Defines a command 'run_anomaly_pipeline' that executes 
            # the 'main' function inside 'anomaly_pipeline.main' module.
            'run_anomaly_pipeline = anomaly_pipeline.main:timeseries_anomaly_detection',
        ],
    },
)

