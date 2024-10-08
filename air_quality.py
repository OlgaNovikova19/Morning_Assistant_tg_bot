import requests
import logging
import datetime

URL_AIR_QUALITY_API = 'https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&hourly=pm10,pm2_5'
URL_GEOCODING_API = 'https://geocoding-api.open-meteo.com/v1/search'
#URL_WATER_QUALITY_API = 'https://api.meersens.com/environment/public/water/current'


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
    print(coordinates)
    params = {'current': ['uv_index', 'pm10', 'pm2_5', 'dust', 'carbon_monoxide', 'european_aqi']}
    params.update(coordinates)
    print(params)
    try:
        response = requests.get(URL_AIR_QUALITY_API, params=params)
        logging.info(f"API AIR QUALITY returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        for x in response_data:
            print (x)

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return




city_coordinates = get_coordinates_by_city_name("Eindhoven", "Netherlands")
get_allergens(city_coordinates)
