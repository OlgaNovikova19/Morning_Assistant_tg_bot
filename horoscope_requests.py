import requests
import logging
import datetime

URL_HOROSCOPE_API = 'https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


def define_zodiac_sign(day: str|None, month: str|None) -> str:
    astro_sign = ''
    day = int(day)

    if month == 'december':
        astro_sign = 'sagittarius' if (day < 22) else 'capricorn'

    elif month == 'january':
        astro_sign = 'capricorn' if (day < 20) else 'aquarius'

    elif month == 'february':
        astro_sign = 'aquarius' if (day < 19) else 'pisces'

    elif month == 'march':
        astro_sign = 'pisces' if (day < 21) else 'aries'

    elif month == 'april':
        astro_sign = 'aries' if (day < 20) else 'taurus'

    elif month == 'may':
        astro_sign = 'taurus' if (day < 21) else 'gemini'

    elif month == 'june':
        astro_sign = 'gemini' if (day < 21) else 'cancer'

    elif month == 'july':
        astro_sign = 'cancer' if (day < 23) else 'leo'

    elif month == 'august':
        astro_sign = 'leo' if (day < 23) else 'virgo'

    elif month == 'september':
        astro_sign = 'Virgo' if (day < 23) else 'libra'

    elif month == 'october':
        astro_sign = 'Libra' if (day < 23) else 'scorpio'

    elif month == 'november':
        astro_sign = 'scorpio' if (day < 22) else 'sagittarius'

    else:
        logging.error('incorrect input day or month of birth ')


    return astro_sign


def get_today_horoscope(day_birth: str|None = None, month_birth: str|None = None, zodiac_sign_val:str|None = None):

    logging.info('function called get_today_horoscope(day: str|None, month: str|None, zodiac_sign_val:str|None')
    if month_birth is not None and day_birth is not None:
        zodiac_sign = define_zodiac_sign(day_birth, month_birth)
        day = int(day_birth)
        if month_birth.isnumeric():
            month_birth = int(month_birth)
        else:
            month_birth = month_birth.lower()
    else:
        if zodiac_sign_val is None:
            logging.error('function called get_today_horoscope(day: str|None, month: str|None, zodiac_sign_val:str|None), all parameters are None')
            return
        else:
            zodiac_sign = zodiac_sign_val

    today_date_formatted = datetime.datetime.today().strftime('%Y-%m-%d')
    params = {'sign': zodiac_sign, 'day':  today_date_formatted}
    try:
        response = requests.get(URL_HOROSCOPE_API, params=params)
        logging.info(f"API HOROSCOPE returned {response.json()}")
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return