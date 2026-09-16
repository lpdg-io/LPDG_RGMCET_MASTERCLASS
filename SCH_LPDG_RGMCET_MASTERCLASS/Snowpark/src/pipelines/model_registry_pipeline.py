
"""
End-to-End Model Registry Pipeline

Workflow:
1. Build features from the weather table
2. Split chronologically into train and test
3. Train a Random Forest
4. Evaluate on the held-out test split
5. Register the model as the next version

Re-running this registers V1, V2, V3, ... automatically. Promotion to
the default version stays manual, so a weaker model never takes over
on its own.
"""
from config.model_config import *

from utils.feature_engineering import (
    build_features,
    split_by_time,
)

from utils.model_trainer import (
    train_model,
)

from utils.model_evaluator import (
    evaluate_model,
)

from utils.model_registry import (
    get_registry,
    next_version_name,
    register_model,
)


def run(session):

    feature_df = build_features(
        session=session,
        table_name=SOURCE_TABLE,
        target_col=TARGET_COLUMN,
    )

    train_df, test_df = split_by_time(
        feature_df
    )

    print(
        f"Training rows: {train_df.count()} | "
        f"Test rows: {test_df.count()}"
    )

    model = train_model(train_df)

    predictions, metrics = evaluate_model(
        model=model,
        test_df=test_df,
    )

    registry = get_registry(session)

    version_name = next_version_name(
        registry=registry,
        model_name=MODEL_NAME,
    )

    register_model(
        registry=registry,
        model=model,
        model_name=MODEL_NAME,
        version_name=version_name,
        sample_input_df=train_df.select(*FEATURE_COLUMNS).limit(5),
        metrics=metrics,
    )

    print(
        f"Registered {MODEL_NAME} / {version_name} "
        f"with metrics {metrics}"
    )

    return version_name, metrics
