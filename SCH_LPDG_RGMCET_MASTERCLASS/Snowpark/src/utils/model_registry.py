"""
Snowflake Model Registry helpers.

Covers registering new versions, listing what exists, and choosing
which version serves predictions.
"""

from snowflake.ml.registry import Registry


def get_registry(session):
    """Return a Registry bound to the session's current database and schema."""
    return Registry(session=session)


def next_version_name(registry, model_name):
    """Return the next version name, e.g. V1 -> V2. A new model starts at V1."""
    try:
        existing = registry.get_model(model_name).show_versions()["name"].tolist()
    except Exception:
        # Model is not registered yet
        return "V1"

    numbers = [
        int(name[1:])
        for name in existing
        if name.startswith("V") and name[1:].isdigit()
    ]

    return f"V{max(numbers) + 1}" if numbers else "V1"


def register_model(
    registry,
    model,
    model_name,
    version_name,
    sample_input_df,
    metrics=None,
):
    """Log a model as a new version, with its metrics attached."""
    return registry.log_model(
        model,
        model_name=model_name,
        version_name=version_name,
        sample_input_data=sample_input_df,
        metrics=metrics or {},
    )


def list_versions(registry, model_name):
    """Return every registered version with its metadata and metrics."""
    return registry.get_model(model_name).show_versions()


def get_serving_version(registry, model_name, version_name=None):
    """Return a model version -- the default one unless a version is named."""
    model = registry.get_model(model_name)

    return model.version(version_name) if version_name else model.default


def set_default_version(registry, model_name, version_name):
    """Promote a version so it serves whenever no version is named."""
    registry.get_model(model_name).default = version_name
