"""
Build forecasting features from the raw weather table.

Training and inference both call build_features(), so the model always
sees features built the exact same way.
"""

from snowflake.snowpark import Window
from snowflake.snowpark import functions as F

from config.model_config import (
    COLUMNS_TO_DROP,
    N_LAGS,
    OTHER_SENSOR_COLS,
    SPLIT_FRACTION,
)


def clean_weather_data(df, target_col):
    """Fix types, drop null targets and duplicates, remove metadata, sort by time."""
    df = df.select([F.col(c).alias(c.upper()) for c in df.columns])

    df = df.with_column(
        "TIMESTAMP",
        F.to_timestamp_ntz(F.col("TIMESTAMP")),
    )

    df = df.filter(F.col(target_col).is_not_null()).distinct()

    df = df.drop(*[c for c in COLUMNS_TO_DROP if c in df.columns])

    return df.sort(F.col("TIMESTAMP").asc())


def add_features(df, target_col):
    """Add lag features and hour of day, using past values only."""
    time_window = Window.order_by(F.col("TIMESTAMP").asc())

    for lag in range(1, N_LAGS + 1):
        df = df.with_column(
            f"{target_col}_LAG_{lag}",
            F.lag(F.col(target_col), lag).over(time_window),
        )

    for col in OTHER_SENSOR_COLS:
        df = df.with_column(
            f"{col}_LAG_1",
            F.lag(F.col(col), 1).over(time_window),
        )

    # Hour is known ahead of time, so it is safe to use directly
    return df.with_column("HOUR", F.hour(F.col("TIMESTAMP")))


def drop_warmup_rows(df):
    """Drop the earliest rows, which have no lag history yet."""
    condition = F.lit(True)

    for col in [c for c in df.columns if "_LAG_" in c]:
        condition = condition & F.col(col).is_not_null()

    return df.filter(condition)


def build_features(session, table_name, target_col):
    """Load the raw table and return a model-ready feature DataFrame."""
    df = clean_weather_data(session.table(table_name), target_col)

    return drop_warmup_rows(add_features(df, target_col))


def split_by_time(df, split_fraction=SPLIT_FRACTION):
    """Split chronologically. Forecast data is never shuffled."""
    split_point = int(df.count() * split_fraction)

    numbered = df.with_column(
        "ROW_NUM",
        F.row_number().over(Window.order_by(F.col("TIMESTAMP").asc())),
    )

    train_df = numbered.filter(F.col("ROW_NUM") <= split_point).drop("ROW_NUM")
    test_df = numbered.filter(F.col("ROW_NUM") > split_point).drop("ROW_NUM")

    return train_df, test_df
