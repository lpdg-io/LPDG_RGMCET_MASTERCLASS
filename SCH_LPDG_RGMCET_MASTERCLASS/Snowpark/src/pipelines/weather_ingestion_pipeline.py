
"""
End-to-End Weather Ingestion Pipeline

Workflow:
1. Fetch data from Open-Meteo
2. Transform JSON into DataFrame
3. Add metadata columns
4. Load data into Snowflake
"""
from config.weather_config import *

from utils.weather_api import (
    fetch_weather_data,
)

from utils.weather_transformer import (
    transform_weather_json,
)

from utils.snowflake_loader import (
    load_to_snowflake,
)


def run(session):

    weather_json = fetch_weather_data(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        start_date=START_DATE,
        end_date=END_DATE,
        hourly_features=HOURLY_FEATURES,
    )

    df = transform_weather_json(
        weather_json
    )

    load_to_snowflake(
        session=session,
        dataframe=df,
        table_name="TBL_WEATHER_DATA",
    )

    print(df.head())