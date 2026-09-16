
"""
End-to-End Model Inference Pipeline

Workflow:
1. Load the serving model version from the registry
2. Load new, unseen data from Snowflake
3. Predict inside Snowflake
4. Return the predictions

With no version_name given, the registry's default version serves.
Promoting a new default therefore changes what runs here, with no
code change.
"""
from snowflake.snowpark import functions as F

from config.model_config import *

from utils.model_registry import (
    get_registry,
    get_serving_version,
)


def load_new_data(session, table_name=TEST_TABLE_NAME, n_rows=10):
    """Load the most recent unseen rows from a Snowflake table."""
    new_data_df = (
        session.table(table_name)
        .sort(F.col("TIMESTAMP").desc())
        .limit(n_rows)
    )

    print(f"Loaded {new_data_df.count()} new rows from {table_name}")

    return new_data_df


def run(session, version_name=None, n_rows=10, table_name=TEST_TABLE_NAME):

    registry = get_registry(session)

    version = get_serving_version(
        registry=registry,
        model_name=MODEL_NAME,
        version_name=version_name,
    )

    print(f"Serving: {MODEL_NAME} / {version.version_name}")

    new_data_df = load_new_data(
        session=session,
        table_name=table_name,
        n_rows=n_rows,
    )

    predictions = version.run(
        new_data_df,
        function_name="predict",
    )

    return predictions.select(
        "TIMESTAMP",
        TARGET_COLUMN,
        PREDICTION_COLUMN,
    )
