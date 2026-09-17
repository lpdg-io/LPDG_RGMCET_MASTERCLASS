CREATE OR REPLACE PROCEDURE TRAIN_MODEL()
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-ml-python')
HANDLER = 'train_and_evaluate'
EXECUTE AS OWNER
AS
$$
from snowflake.snowpark.context import get_active_session
from snowflake.ml.modeling.ensemble import RandomForestRegressor
from snowflake.ml.modeling.metrics import mean_absolute_error, r2_score
from snowflake.ml.registry import Registry

# --- Config (from config/model_config.py) ---
TRAIN_TABLE       = "WEATHER_TRAIN"
TEST_TABLE        = "WEATHER_TEST"
TARGET_COLUMN     = "TEMPERATURE"
PREDICTION_COLUMN = "PREDICTED_TEMPERATURE"
MODEL_NAME        = "WEATHER_TEMPERATURE_MODEL"
N_ESTIMATORS      = 100
RANDOM_STATE      = 42
N_LAGS            = 3
OTHER_SENSOR_COLS = ["HUMIDITY", "PRESSURE", "WIND_SPEED", "PRECIPITATION", "CLOUD_COVER"]
FEATURE_COLUMNS   = (
    [f"{TARGET_COLUMN}_LAG_{lag}" for lag in range(1, N_LAGS + 1)]
    + ["HOUR"]
    + [f"{c}_LAG_1" for c in OTHER_SENSOR_COLS]
)


def train_model(train_df):
    model = RandomForestRegressor(
        input_cols=FEATURE_COLUMNS,
        label_cols=[TARGET_COLUMN],
        output_cols=[PREDICTION_COLUMN],
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
    )
    model.fit(train_df)
    return model


def evaluate_model(model, test_df):
    predictions = model.predict(test_df)
    mae = mean_absolute_error(df=predictions, y_true_col_names=TARGET_COLUMN,
                              y_pred_col_names=PREDICTION_COLUMN)
    r2 = r2_score(df=predictions, y_true_col_name=TARGET_COLUMN,
                  y_pred_col_name=PREDICTION_COLUMN)
    return float(mae), float(r2)


def train_and_evaluate():
    session = get_active_session()

    train_df = session.table(TRAIN_TABLE)
    test_df = session.table(TEST_TABLE)

    model = train_model(train_df)
    mae, r2 = evaluate_model(model, test_df)

    # Register the model in the Snowflake Model Registry.
    # version_name has to be unique per model_name, so we timestamp it --
    # this avoids the procedure failing on a second run with the same version.
    registry = Registry(session=session)
    from datetime import datetime
    version_name = "V" + datetime.now().strftime("%Y%m%d_%H%M%S")

    registry.log_model(
        model,
        model_name=MODEL_NAME,
        version_name=version_name,
        sample_input_data=train_df.limit(10),
        metrics={"mae": mae, "r2": r2},
    )

    return (f"Training complete. MAE={mae:.2f}, R2={r2:.3f}. "
            f"Registered as {MODEL_NAME} version {version_name}.")
$$;