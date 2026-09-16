"""
Configuration file for Model Registry and Inference.

Students can modify:
- Model name
- Lag depth and sensor columns
- Train/test split ratio
- Random Forest settings

without changing the pipeline code.
"""

from pathlib import Path

# Table created by the weather ingestion pipeline
SOURCE_TABLE = "TBL_WEATHER_DATA"

# Name the model is registered under in the Snowflake Model Registry
MODEL_NAME = "WEATHER_TEMPERATURE_MODEL"

# What we forecast, and the column the model writes its prediction into
TARGET_COLUMN = "TEMPERATURE"
PREDICTION_COLUMN = "PREDICTED_TEMPERATURE"

# Station metadata: identical on every row for a single location,
# so it cannot help predict anything
COLUMNS_TO_DROP = ["LATITUDE", "LONGITUDE", "TIMEZONE", "ELEVATION"]

# Sensors whose previous-hour reading helps explain temperature
OTHER_SENSOR_COLS = [
    "HUMIDITY",
    "PRESSURE",
    "WIND_SPEED",
    "PRECIPITATION",
    "CLOUD_COVER",
]

# How many past hours of temperature the model looks back on
N_LAGS = 3

# Every feature is a past value or a known-in-advance value (HOUR),
# so the model never sees the hour it is predicting
FEATURE_COLUMNS = (
    [f"{TARGET_COLUMN}_LAG_{lag}" for lag in range(1, N_LAGS + 1)]
    + ["HOUR"]
    + [f"{col}_LAG_1" for col in OTHER_SENSOR_COLS]
)

# Train on the earliest 80% of the timeline, test on the most recent 20%
SPLIT_FRACTION = 0.8

# Random Forest settings
N_ESTIMATORS = 100
RANDOM_STATE = 42

# Held-out data used to demonstrate inference
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
TEST_DATA_PATH = DATA_DIR / "test_data.csv"
