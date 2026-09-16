
"""
End-to-End Model Inference Pipeline

Workflow:
1. Load the serving model version from the registry
2. Load new, unseen data
3. Predict inside Snowflake
4. Return the predictions

With no version_name given, the registry's default version serves.
Promoting a new default therefore changes what runs here, with no
code change.
"""
import pandas as pd

from config.model_config import *

from utils.model_registry import (
    get_registry,
    get_serving_version,
)


def load_new_data(session, csv_path=TEST_DATA_PATH, n_rows=10):
    """Load unseen rows from CSV as a Snowpark DataFrame."""
    new_data_pdf = (
        pd.read_csv(csv_path)
        .sort_values("TIMESTAMP")
        .tail(n_rows)
    )

    print(f"Loaded {len(new_data_pdf)} new rows")

    return session.create_dataframe(new_data_pdf)


def run(session, version_name=None, n_rows=10, csv_path=TEST_DATA_PATH):

    registry = get_registry(session)

    version = get_serving_version(
        registry=registry,
        model_name=MODEL_NAME,
        version_name=version_name,
    )

    print(f"Serving: {MODEL_NAME} / {version.version_name}")

    new_data_df = load_new_data(
        session=session,
        csv_path=csv_path,
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
