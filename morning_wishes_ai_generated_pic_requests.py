import requests
import logging
import datetime
from Secrets import secrets
import json
import time

URL_KANDINSKIY_API = 'https://api-key.fusionbrain.ai/'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

AUTH_HEADERS = {
        'X-Key': f'Key {secrets.KANDINSKIY_API_KEY}',
        'X-Secret': f'Secret {secrets.KANDINSKIY_API_SECRET_KEY}',
    }

def get_model():
    response = requests.get(URL_KANDINSKIY_API + 'key/api/v1/models', headers=AUTH_HEADERS)
    data = response.json()
    return data[0]['id']


def generate(text, model, images=1, width=1024, height=1024):
    params = {"type": "GENERATE", "numImages": 1, "width": 1024, "height": 1024, "generateParams": {"query": f"{text}"}}
    data = {
        'model_id': (None, model),
        'params': (None, json.dumps(params), 'application/json')
    }
    response = requests.post(URL_KANDINSKIY_API + 'key/api/v1/text2image/run', headers=AUTH_HEADERS, files=data)
    data = response.json()
    return data['uuid']


def check_generation(request_id, attempts=10, delay=10):
    while attempts > 0:
        response = requests.get(URL_KANDINSKIY_API + 'key/api/v1/text2image/status/' + request_id, headers=AUTH_HEADERS)
        data = response.json()
        if data['status'] == 'DONE':
            return data['images']

        attempts -= 1
        time.sleep(delay)

def get_ai_generated_pic_for_text(text:str) ->str|None:
    try:
        model_id = get_model()
        request_id = generate(text, model_id)
        images = check_generation(request_id)
        # returns  Base64-encoded string
        return images[0]


    except requests.exceptions.RequestException or ValueError as e:
        logging.error(e)
        return
