import logging
import requests
from Secrets import secrets
import os
import google.generativeai as genai

os.environ["API_KEY"] = secrets.GOOGLE_AI_API_KEY

genai.configure(api_key=os.environ["API_KEY"])

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)
def make_google_api_request(subject_of_interest, results):
    model = genai.GenerativeModel("gemini-1.5-flash")
    retries = 3
    for _ in range(retries):
        try:
            response = model.generate_content(f"write evaluation of {subject_of_interest} on the basis of {results}")
            logging.info(f'GOOGLE AI API returned response.text: {response}')
            #print(response.text)
            return response.text

        except Exception as e:
            if e == 'Unknown field for Candidate: finish_reason':
                return 'It seems like AI considered your request as unappropriate..Sometimes it happens if the historical event tragic or due to some other reasons'
            else:
                return "Try once again later. It wasn`t possible to get necessary data"
            logging.error(e)

