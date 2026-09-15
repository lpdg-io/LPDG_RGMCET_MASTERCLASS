
"""
Transform API JSON response into a structured dataframe.

This step converts nested JSON into a tabular format
that can be loaded into Snowflake.
"""
import pandas as pd
from datetime import datetime


def transform_weather_json(weather_json):
    df = pd.DataFrame(weather_json["hourly"])

    df.rename(
        columns={"time": "timestamp"},
        inplace=True
    )

    df["latitude"] = weather_json["latitude"]
    df["longitude"] = weather_json["longitude"]
    df["timezone"] = weather_json["timezone"]
    df["timezone_abbreviation"] = (
        weather_json["timezone_abbreviation"]
    )
    df["elevation"] = weather_json["elevation"]

    df["load_timestamp"] = datetime.utcnow()

    return df