import requests
import logging
import datetime
from Secrets import secrets

URL_HISTORICAL_EVENTS_TODAY_API = 'https://api.api-ninjas.com/v1/historicalevents'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


def get_historical_events_for_today(limiting_subject=None):
    today = datetime.datetime.today()
    current_month_str = today.strftime("%m")
    current_day_str = today.strftime("%d")
    headers = {'X-Api-Key': secrets.HISTORICAL_EVENTS_API_KEY}
    params = {'month': current_month_str, 'day': current_day_str, 'text':limiting_subject}
    try:
        response = requests.get(URL_HISTORICAL_EVENTS_TODAY_API, headers=headers, params=params)
        response.raise_for_status()
        try:
            response_data = response.json()
            logging.info(f"API HISTORICAL EVENTS returned {response.json()}")

        except ValueError as e:
            logging.error(e)
            return

        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return
