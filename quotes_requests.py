import requests
import logging
from Secrets import secrets
import datetime

URL_QUOTES_API = 'https://api.api-ninjas.com/v1/quotes?category={}'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


def get_quotes(category):
    logging.info(f'function called: get_quotes(category) with arg category= {category}')
    headers = {'X-Api-Key': secrets.QUOTES_API_KEY}
    try:
        response = requests.get(URL_QUOTES_API.format(category), headers=headers)
        logging.info(f"QUOTES_API returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return
