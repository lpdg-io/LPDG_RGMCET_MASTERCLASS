"""
Configuration file for Weather Data Ingestion.

Students can modify:
- Latitude
- Longitude
- Date Range
- Features to Fetch

without changing the pipeline code.
"""

from datetime import date, timedelta

# Hyderabad Coordinates
LATITUDE = 17.3850
LONGITUDE = 78.4867

# Fetch last 60 days of data
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=60)

# Weather variables requested from Open-Meteo
HOURLY_FEATURES = [
    "temperature_2m",
    "relative_humidity_2m",
    "pressure_msl",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "precipitation",
    "cloud_cover",
    "dew_point_2m",
    "apparent_temperature",
    "weather_code"
]