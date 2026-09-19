CREATE OR REPLACE PROCEDURE BUILD_TRAINING_DATA()
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'build_training_data'
EXECUTE AS OWNER
AS
$$
from snowflake.snowpark import Window
from snowflake.snowpark import functions as F
from snowflake.snowpark.context import get_active_session

# --- Config (from config/model_config.py) --- commit test from branch
SOURCE_TABLE      = "TBL_WEATHER_DATA"
TARGET_COLUMN     = "TEMPERATURE"
COLUMNS_TO_DROP   = ["LATITUDE", "LONGITUDE", "TIMEZONE", "ELEVATION"]
OTHER_SENSOR_COLS = ["HUMIDITY", "PRESSURE", "WIND_SPEED", "PRECIPITATION", "CLOUD_COVER"]
N_LAGS            = 3
SPLIT_FRACTION    = 0.8
TRAIN_TABLE       = "WEATHER_TRAIN"
TEST_TABLE        = "WEATHER_TEST"


def clean_weather_data(df, target_col):
    df = df.select([F.col(c).alias(c.upper()) for c in df.columns])
    df = df.with_column("TIMESTAMP", F.to_timestamp_ntz(F.col("TIMESTAMP")))
    df = df.filter(F.col(target_col).is_not_null()).distinct()
    df = df.drop(*[c for c in COLUMNS_TO_DROP if c in df.columns])
    return df.sort(F.col("TIMESTAMP").asc())


def add_features(df, target_col):
    time_window = Window.order_by(F.col("TIMESTAMP").asc())

    for lag in range(1, N_LAGS + 1):
        df = df.with_column(f"{target_col}_LAG_{lag}",
                            F.lag(F.col(target_col), lag).over(time_window))

    for col in OTHER_SENSOR_COLS:
        df = df.with_column(f"{col}_LAG_1", F.lag(F.col(col), 1).over(time_window))

    return df.with_column("HOUR", F.hour(F.col("TIMESTAMP")))


def drop_warmup_rows(df):
    condition = F.lit(True)
    for col in [c for c in df.columns if "_LAG_" in c]:
        condition = condition & F.col(col).is_not_null()
    return df.filter(condition)


def split_by_time(df, split_fraction):
    split_point = int(df.count() * split_fraction)
    numbered = df.with_column(
        "ROW_NUM",
        F.row_number().over(Window.order_by(F.col("TIMESTAMP").asc())),
    )
    train_df = numbered.filter(F.col("ROW_NUM") <= split_point).drop("ROW_NUM")
    test_df  = numbered.filter(F.col("ROW_NUM") >  split_point).drop("ROW_NUM")
    return train_df, test_df


def build_training_data():
    session = get_active_session()

    df = session.table(SOURCE_TABLE)
    df = clean_weather_data(df, TARGET_COLUMN)
    df = add_features(df, TARGET_COLUMN)
    df = drop_warmup_rows(df)

    train_df, test_df = split_by_time(df, SPLIT_FRACTION)

    train_df.write.mode("overwrite").save_as_table(TRAIN_TABLE)
    test_df.write.mode("overwrite").save_as_table(TEST_TABLE)

    return (f"Feature build complete. "
            f"Train rows: {train_df.count()}, Test rows: {test_df.count()}. "
            f"Written to {TRAIN_TABLE} and {TEST_TABLE}.")
$$;