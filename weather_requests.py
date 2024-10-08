import requests
import logging
import datetime

URL_AIR_QUALITY_API = 'https://air-quality-api.open-meteo.com/v1/air-quality'
URL_GEOCODING_API = 'https://geocoding-api.open-meteo.com/v1/search'
URL_WEATHER_CURRENT_API = 'https://api.open-meteo.com/v1/forecast'
URL_SUNRISE_SUNSET_DATA_API = 'https://api.open-meteo.com/v1/forecast'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


def get_coordinates_by_city_name(city_name: str, country: str) -> dict | None:
    params = {'name': city_name}
    try:
        response = requests.get(URL_GEOCODING_API, params)
        logging.info(f"API GEOCODING returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        response_data_res = response_data['results']
        for data_unit in response_data_res:
            if data_unit['country'] == country:
                return {'latitude': data_unit['latitude'], 'longitude': data_unit['longitude']}
            else:
                logging.info("Incorrect input of the city name or the country name")
                return
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return


def get_allergens(coordinates: dict):
    logging.info(f'function called: get_allergens(coordinates: dict) with args coordinates = {coordinates}')
    params = {'current': ['uv_index', 'pm10', 'pm2_5', 'dust', 'carbon_monoxide', 'european_aqi'], 'timezone': 'auto'}
    params.update(coordinates)
    try:
        response = requests.get(URL_AIR_QUALITY_API, params=params)
        logging.info(f"API AIR QUALITY returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return


def get_current_weather_conditions(coordinates: dict):
    logging.info(
        f'function called: get_current_weather_conditions(coordinates: dict) with args coordinates = {coordinates}')
    params = {
        'current': ['temperature_2m', 'relative_humidity_2m,apparent_temperature', 'precipitation', 'rain', 'showers',
                    'snowfall', 'weather_code', 'cloud_cover', 'wind_speed_10m', 'wind_direction_10m,wind_gusts_10m'], 'timezone': 'auto'}
    params.update(coordinates)
    try:
        response = requests.get(URL_WEATHER_CURRENT_API, params=params)
        logging.info(f"API SUNRISE_SUNSET_DATA_API returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return


def get_sunrise_sunset_data(coordinates: dict):
    logging.info(
        f'function called: get_sunrise_sunset_data(coordinates: dict) with args coordinates = {coordinates}')
    params = {
        'daily': ['sunrise', 'sunset', 'daylight_duration', 'sunshine_duration'], 'timezone': 'auto'}
    params.update(coordinates)
    try:
        response = requests.get(URL_WEATHER_CURRENT_API, params=params)
        logging.info(f"API WEATHER_CURRENT returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return

#city_coordinates = get_coordinates_by_city_name("Eindhoven", "Netherlands")
#get_allergens(city_coordinates)
