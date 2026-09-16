"""
Train the temperature forecasting model.

Training runs inside Snowflake on a Snowpark DataFrame, so the data
never leaves the warehouse.
"""

from snowflake.ml.modeling.ensemble import RandomForestRegressor

from config.model_config import (
    FEATURE_COLUMNS,
    N_ESTIMATORS,
    PREDICTION_COLUMN,
    RANDOM_STATE,
    TARGET_COLUMN,
)


def train_model(train_df):
    """Fit a Random Forest on the training split and return the model."""
    model = RandomForestRegressor(
        input_cols=FEATURE_COLUMNS,
        label_cols=[TARGET_COLUMN],
        output_cols=[PREDICTION_COLUMN],
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
    )

    model.fit(train_df)

    return model
