"""
Utility functions for interacting with the Open-Meteo API.
"""

import requests


def fetch_weather_data(
    latitude,
    longitude,
    start_date,
    end_date,
    hourly_features,
):
    """
    Fetch historical weather data.

    Parameters
    ----------
    latitude : float
        Latitude of the location.

    longitude : float
        Longitude of the location.

    start_date : str
        Start date in YYYY-MM-DD format.

    end_date : str
        End date in YYYY-MM-DD format.

    hourly_features : list
        Weather variables to retrieve.

    Returns
    -------
    dict
        JSON response from Open-Meteo.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"

    url = (
        f"{base_url}"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&hourly={','.join(hourly_features)}"
    )

    response = requests.get(url)
    response.raise_for_status()

    return response.json()