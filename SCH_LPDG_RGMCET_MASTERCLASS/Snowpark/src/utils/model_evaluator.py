"""
Score model predictions against the true values.

Metrics are calculated inside Snowflake on Snowpark DataFrames.
"""

from snowflake.ml.modeling.metrics import mean_absolute_error, r2_score

from config.model_config import PREDICTION_COLUMN, TARGET_COLUMN


def evaluate_model(model, test_df):
    """Predict on the test split and return (predictions, metrics)."""
    predictions = model.predict(test_df)

    mae = mean_absolute_error(
        df=predictions,
        y_true_col_names=TARGET_COLUMN,
        y_pred_col_names=PREDICTION_COLUMN,
    )

    r2 = r2_score(
        df=predictions,
        y_true_col_name=TARGET_COLUMN,
        y_pred_col_name=PREDICTION_COLUMN,
    )

    print(f"MAE : {mae:.2f} degrees")
    print(f"R2  : {r2:.3f}")

    # Cast to plain floats so the registry can store them as JSON
    metrics = {"mae": float(mae), "r2": float(r2)}

    return predictions, metrics
