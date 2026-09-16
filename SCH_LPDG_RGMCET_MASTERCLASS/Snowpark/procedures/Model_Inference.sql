CREATE OR REPLACE PROCEDURE RUN_INFERENCE(
    INPUT_TABLE VARCHAR DEFAULT 'TBL_WEATHER_TEST_DATA',
    OUTPUT_TABLE VARCHAR DEFAULT 'WEATHER_PREDICTIONS'
)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-ml-python')
HANDLER = 'run_inference'
EXECUTE AS OWNER
AS
$$
from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import Registry

# --- Config (from config/model_config.py) ---
MODEL_NAME = "WEATHER_TEMPERATURE_MODEL"


def run_inference(input_table, output_table):
    session = get_active_session()

    # -- No version given -> serves whichever version is currently the default ---
    registry = Registry(session=session)
    version = registry.get_model(MODEL_NAME).default

    new_data_df = session.table(input_table)
    predictions = version.run(new_data_df, function_name="predict")

    predictions.write.mode("overwrite").save_as_table(output_table)

    return (f"Inference complete using {MODEL_NAME} / {version.version_name}. "
            f"Predicted {predictions.count()} rows from {input_table} into {output_table}.")
$$;
