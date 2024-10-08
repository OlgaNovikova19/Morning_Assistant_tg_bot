import calendar
import datetime
import json
from io import BytesIO

import database_actions
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Secrets import secrets
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, utils, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuildergit status
from aiogram.types import ReplyKeyboardRemove, Update, InputFile, file
from aiogram.handlers import CallbackQueryHandler
from weather_requests import get_allergens, get_current_weather_conditions, get_sunrise_sunset_data
from google_ai_api_requests import make_google_api_request
import markdown
from bs4 import BeautifulSoup
from aiogram.enums import ParseMode
import re
from horoscope_requests import get_today_horoscope
from quotes_requests import get_quotes
import emoji
from PIL import Image, ImageDraw, ImageFont
from text_overlay_on_image import add_text_to_image
from aiogram.types import BufferedInputFile
from historical_events_today_requests import get_historical_events_for_today
from database_actions import select_random_pic_for_overlay__copy__one_modify_by_overlaying_text__and_delete, get_path_morning_wishes_pic, audio_paths
from morning_wishes_pic_requests import get_pic_generated
from morning_wishes_ai_generated_pic_requests import get_ai_generated_pic_for_text
import base64

dp = Dispatcher()
SESSION = {}
year_event = asyncio.Event()
font_selected_event = asyncio.Event()
font_colour_selected_event = asyncio.Event()



class HoroscopeState():
    _day_ = ''
    _month_ = ''
    _year_ = ''
    _zodiac_sign_ = ''

    @property
    def day(self):
        return self._day_

    @day.setter
    def day(self, another_day):
        self._day_ = another_day

    @property
    def month(self):
        return self._month_

    @month.setter
    def month(self, another_month):
        self._month_ = another_month

    @property
    def year(self):
        return self._year_

    @year.setter
    def year(self, another_year):
        self._year_ = another_year

    @property
    def zodiac_sign(self):
        return self._zodiac_sign_

    @zodiac_sign.setter
    def zodiac_sign(self, another_zodiac_sign):
        self._zodiac_sign_ = another_zodiac_sign


class InterestingTypeHistoricalEvents(StatesGroup):
    type_of_historical_event = State()
    index_of_historical_event = State()

class CreatingMorningWishesPic(StatesGroup):
    instructions_for_AI = State()
    text_overlay = State()



bot = Bot(token=secrets.TELEGRAM_TOKEN, default=DefaultBotProperties(
    parse_mode='Markdown'))

horoscope_data = HoroscopeState()

ZODIAC_SIGNS = ['sagittarius', 'capricorn', 'aquarius', 'pisces', 'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                'libra', 'scorpio']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
          'december']


async def main() -> None:
    await dp.start_polling(bot)


def create_buttons(buttons_data_list=None, adjust_number=1):
    logging.info('function create_buttons(buttons_data_list=None, adjust_number=1) was called')

    if buttons_data_list is not None:
        builder = InlineKeyboardBuilder()
        for i in buttons_data_list:
            button_index = types.InlineKeyboardButton(text=f"{i}", callback_data=f'{i}')
            builder.add(button_index)
        builder.adjust(adjust_number)
        reply_markup_ = builder.as_markup(resize_keyboard=True)
        return reply_markup_
    else:
        logging.info('buttons_data_list is None')
    return


"""@dp.message(Command("/start"))
async def message_handler_greetings(message: types.Message) -> None:
    print('ok')
    print(message.text)
    await message.answer('Hello')"""




"""async def update_handler(update: Update, bot: Bot, dispatcher: Dispatcher):
    result = await dp.feed_update(bot, update)"""


@dp.callback_query(F.data.startswith('Get weather'))
async def prepare(callback: types.CallbackQuery):
    print('callback is called')
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Send geolocation", request_location=True))
    builder.adjust(1)
    reply_markup_ = builder.as_markup(resize_keyboard=True)
    await callback.message.answer("Please send your location", show_alert=True, reply_markup=reply_markup_)


@dp.callback_query(F.data.startswith('Get current weather'))
async def output_current_weather(callback: types.CallbackQuery):
    logging.info(f'callback is called')
    print(f'callback is called')
    coord_dict = SESSION['Location']
    print(coord_dict)
    current_weather_response = get_current_weather_conditions(coord_dict)
    current_weather_data_dict = current_weather_response['current']
    ai_text_current_weather = make_google_api_request('current weather conditions', current_weather_data_dict)
    formatted_text = re.sub(r'\#\# ', ' ', ai_text_current_weather)
    formatted_text = re.sub(r'\* ', ' ', formatted_text)
    formatted_text = re.sub(r'\*\*', '* ', formatted_text)

    await callback.message.answer(formatted_text, show_alert=True)


@dp.callback_query(F.data.startswith('Get current air'))
async def output_current_air_quality(callback: types.CallbackQuery):
    logging.info(f'callback is called')
    print(f'callback is called with F.data {F.data}')
    coord_dict = SESSION['Location']

    allergens_today_response = get_allergens(coord_dict)
    ai_text = make_google_api_request('current air quality', allergens_today_response['current'])
    formatted_text = re.sub(r'\#\# ', ' ', ai_text)
    formatted_text = re.sub(r'\* ', ' ', formatted_text)
    formatted_text = re.sub(r'\*\*', '* ', formatted_text)

    await callback.message.answer(formatted_text, show_alert=True)


@dp.callback_query(F.data.startswith('Get sunset/sunrise'))
async def output_sunset_sunrise_time(callback: types.CallbackQuery):
    logging.info(f'callback is called')
    print(f'callback is called')
    coord_dict = SESSION['Location']
    today = datetime.datetime.today()
    print(coord_dict, 'coord')
    print(get_sunrise_sunset_data(coord_dict))

    sunrise_today = get_sunrise_sunset_data(coord_dict)['daily']['sunrise'][0]
    sunrise_today_str = str(sunrise_today).split('T')[1]
    sunset_today = get_sunrise_sunset_data(coord_dict)['daily']['sunset'][0]
    sunset_today_str = str(sunset_today).split('T')[1]
    daylight_duration_sec = get_sunrise_sunset_data(coord_dict)['daily']['daylight_duration'][0]
    sunshine_duration_sec = get_sunrise_sunset_data(coord_dict)['daily']['sunshine_duration'][0]

    def convert_sec_to_h_min_sec(n):
        return datetime.timedelta(seconds=n)

    daylight_duration_h_min_sec = convert_sec_to_h_min_sec(round(daylight_duration_sec))
    sunshine_duration_h_min_sec = convert_sec_to_h_min_sec(round(sunshine_duration_sec))
    print(get_sunrise_sunset_data(coord_dict))
    sunset_sunrise_response_str = (
        f'TIME OF SUNRISE TODAY: {sunrise_today_str},\n\nTIME OF SUNSET TODAY: {sunset_today_str},\n\n'
        f' DAYLIGHT DURATION TODAY h:m:s : {daylight_duration_h_min_sec},\n\n SUNSHINE DURATION TODAY BECAUSE OF WEATHER CONDITIONS h:m:s : {sunshine_duration_h_min_sec}')

    await callback.message.answer(sunset_sunrise_response_str, show_alert=True)


@dp.callback_query(F.data == 'Get today horoscope')
async def prepare_output_today_horoscope(callback: types.CallbackQuery):
    logging.info(f'callback is called from button:"Get today horoscope"')
    print(f'callback is called')
    question_know_my_zodiac_sign_markup_ = create_buttons(["I know my zodiac sign", "I don`t know my zodiac sign"], 2)
    await callback.message.answer("Do you know your zodiac sign?", reply_markup=question_know_my_zodiac_sign_markup_)


@dp.callback_query(F.data == 'I know my zodiac sign')
async def output_know_zodiac_sign(callback: types.CallbackQuery):
    logging.info(f'callback is called from button:"I know my zodiac sign"')
    print(f'callback is called')

    zodiac_signs_markup_ = create_buttons(ZODIAC_SIGNS, 4)
    await callback.message.answer("Do you know your zodiac sign?", reply_markup=zodiac_signs_markup_)
    filter_registrate_zodiac_sign()
    print(horoscope_data.zodiac_sign, 'horoscope_data.zodiac_sign')
    print(type(horoscope_data.zodiac_sign))


#aiogram==3.13.1 doesn`t support another way to install filter in this case
def filter_registrate_zodiac_sign():
    for sign in ZODIAC_SIGNS:
        @dp.callback_query(F.data == sign)
        async def save_zodiac_sign(callback: types.CallbackQuery):
            horoscope_data.zodiac_sign = callback.data
            horoscope_resp = get_today_horoscope(zodiac_sign_val=horoscope_data.zodiac_sign)
            print(horoscope_resp['data']['horoscope_data'])
            await callback.message.answer(horoscope_resp['data']['horoscope_data'])


@dp.callback_query(F.data == 'I don`t know my zodiac sign')
async def output_not_know_zodiac_sign(callback: types.CallbackQuery):
    logging.info(f'callback is called from button:"I don`t know my zodiac sign"')
    print(f'callback is called')

    numbers_str = [str(number) for number in range(0, 10)]
    ask_year_birth_markup_ = create_buttons(numbers_str, 5)
    #ask_year_birth_markup_ = create_buttons(["SAVE"], 1)
    await callback.message.answer("Use these numbers to put your year of birth in", reply_markup=ask_year_birth_markup_)
    save_year_birth_ask_month_birth(numbers_str)

    await year_event.wait()
    if len(horoscope_data.year) == 4:
        year_event.clear()
        cancel_markup = create_buttons(['CANCEL', 'CONTINUE'], 1)
        await callback.message.answer('Press CANCEL button to delete year if needed', reply_markup=cancel_markup)


def save_year_birth_ask_month_birth(numbers_str):
    for number in numbers_str:
        @dp.callback_query(F.data == number)
        async def year_save(callback: types.CallbackQuery):
            logging.info(f'callback is called from button with number of year of birth')
            if len(horoscope_data.year) < 4:
                horoscope_data.year += callback.data
                await callback.message.answer(f'Year selected {horoscope_data.year}')
            elif len(horoscope_data.year) == 4:
                if 5 <= int(datetime.datetime.today().year) - int(horoscope_data.year) <= 100:
                    year_event.set()
                    await callback.message.answer(
                        "Selected year saved. To cancel select CANCEL button")
                    return

                else:
                    horoscope_data.year = ''
                    await callback.message.answer('Error. Try once again. This year will not be saved')
                    return
            else:
                await callback.message.answer('Error. Try once again. This year will not be saved')



@dp.callback_query(F.data == 'CANCEL')
async def cancel_year_setting(callback: types.CallbackQuery):
    horoscope_data.year = ''
    await callback.message.answer("Set year was deleted. You can try once again")


@dp.callback_query(F.data == 'CONTINUE')
async def continue_after_year_setting(callback: types.CallbackQuery):
    if len(horoscope_data.year) == 4:
        global MONTHS
        reply_markup_registrate_month_birth = create_buttons(MONTHS, 3)
        await callback.message.answer("Type in month of your birth",
                                      reply_markup=reply_markup_registrate_month_birth)

        save_month_birth_ask_day_birth_for_zodiac_sign()
    else:
        await callback.message.answer("Select year to continue")


def save_month_birth_ask_day_birth_for_zodiac_sign():
    for month in MONTHS:
        @dp.callback_query(F.data == month)
        async def month_save_day_ask(callback: types.CallbackQuery):
            logging.info(f'callback is called from button with month of birth')

            horoscope_data.month = callback.data
            number_of_month = datetime.datetime.strptime(callback.data, "%B").month
            _, amount_days_in_month = calendar.monthrange(int(horoscope_data.year), number_of_month)
            upper_range = amount_days_in_month + 1

            days = [str(day) for day in range(1, upper_range)]
            ask_day_birth_markup_ = create_buttons(days, 5)
            await callback.message.answer("Type in day of your birth", reply_markup=ask_day_birth_markup_)
            save_day_birth(days)


def save_day_birth(days):
    print('save_day_birth(days) called')
    for day in days:
        @dp.callback_query(F.data == day)
        async def save_day_ask_horoscope(callback: types.CallbackQuery):
            horoscope_data.day = callback.data
            horoscope_today = get_today_horoscope(horoscope_data.day, horoscope_data.month)
            horoscope_ready = horoscope_today['data']['horoscope_data']
            await callback.message.answer(horoscope_ready)


# all actions for button with callback.data = "Get inspirational_quote"
@dp.callback_query(F.data == "Get inspirational_quote")
async def choose_category_quote(callback: types.CallbackQuery):
    positive_categories = ['morning', 'happiness', 'hope', 'home', 'education', 'dreams', 'faith', 'family',
                           'friendship', 'future', 'inspirational', 'intelligence', 'knowledge', 'love', 'success']
    reply_markup_categories_of_quotes = create_buttons(positive_categories, 3)

    text_with_emoji = emoji.emojize('Select category\nto get an inspirational :open_book:quote:open_book:!')
    await callback.message.answer(
        text_with_emoji,
        reply_markup=reply_markup_categories_of_quotes
    )
    registrate_category_get_quote(positive_categories)


def registrate_category_get_quote(positive_categories):
    logging.info(f"function called 'registrate_category_get_quote called'")
    for category in positive_categories:

        @dp.callback_query(F.data == category)
        async def get_quote(callback: types.CallbackQuery):
            resp_quote = get_quotes(callback.data)
            resp_quote_ready_for_output = f'QUOTE\n {resp_quote[0]['quote']}  \n\nAUTHOR\n  {resp_quote[0]['author']}  \n\nCATEGORY\n  {resp_quote[0]['category']}'

            image_for_text_overlay_path = select_random_pic_for_overlay__copy__one_modify_by_overlaying_text__and_delete()
            output_image_path = add_text_to_image(image_for_text_overlay_path, f"{resp_quote_ready_for_output}",
                                                  image_for_text_overlay_path)

            input_file = types.FSInputFile(output_image_path)

            await callback.message.answer_photo(photo=input_file)

            yes_no = ['yes', 'no']
            reply_markup_comment_quote_ai = create_buttons(yes_no, 1)

            await callback.message.answer(
                'Do you want a comment from AI?',
                reply_markup=reply_markup_comment_quote_ai
            )
            get_ai_comment('quote', resp_quote_ready_for_output)


def get_ai_comment(subject_of_interest, results):
    @dp.callback_query(lambda c: c.data in ['yes', 'no'])
    async def get_comment_from_ai_about_quote(callback: types.CallbackQuery):
        if callback.data == 'no':
            no_resp = "Ok, just enjoy your morning!😀"
            await callback.message.answer(no_resp)
        else:
            ai_text = make_google_api_request(subject_of_interest, results)
            formatted_text = re.sub(r'\#\# ', ' ', ai_text)
            formatted_text = re.sub(r'\* ', ' ', formatted_text)
            formatted_text = re.sub(r'\*\*', '* ', formatted_text)
            await callback.message.answer(
                formatted_text
            )


#all actions connected with selection of button with callback_data == "Get historical events today"
@dp.callback_query(F.data == 'Get historical events today')
async def prepare_markup_to_get_historical_events_today(callback: types.CallbackQuery):
    logging.info('callback is called from button with callback.data == "Get historical events today"')
    historical_events_reply_markup = create_buttons(["Specify historical events", "Not specify historical events"], 2)
    await callback.message.answer(
        'Would you like to specify the type of historical events you are interested in?\nFor example, you could input "Roman Empire".',
        reply_markup=historical_events_reply_markup)

@dp.callback_query(F.data == 'Not specify historical events')
async def prepare_markup_to_get_historical_events_today(callback: types.CallbackQuery, state: FSMContext):
    response_historical_events = get_historical_events_for_today()
    resp_str = ''
    if response_historical_events:
        if len(response_historical_events) > 1:
            for index, hist_event in enumerate(response_historical_events):
                resp_str += f'№ {index+1}\n YEAR: {hist_event["year"]},\nMONTH: {hist_event["month"]},\nDAY: {hist_event["day"]}\n\nEVENT: {hist_event["event"]}\n\n\n'
        else:
            for hist_event in response_historical_events:
                resp_str += f'YEAR: {hist_event["year"]},\nMONTH: {hist_event["month"]},\nDAY: {hist_event["day"]}\n\nEVENT: {hist_event["event"]}\n\n\n'

    else:
        resp_str = "No historical events of the specified type for current day"
    await callback.message.answer(resp_str)
    await callback.message.answer("Would you like to get a comment from AI? Type the number of historical event in.")
    await state.set_state(InterestingTypeHistoricalEvents.index_of_historical_event)
    await state.set_data(response_historical_events)

@dp.callback_query(F.data == 'Specify historical events')
async def prepare_markup_to_get_historical_events_today(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Ok. just input the type of historical events you are interested in as a message')
    await state.set_state(InterestingTypeHistoricalEvents.type_of_historical_event)
    logging.info('state is set InterestingTypeHistoricalEvents.type_of_historical_event')



def formatting_google_ai_response_text(text):
    formatted_text = re.sub(r'\#\# ', ' ', text)
    formatted_text = re.sub(r'\* ', ' ', formatted_text)
    formatted_text = re.sub(r'\*\*', '* ', formatted_text)
    return formatted_text

#specific message handler.
#If making changes - not to place general message handler before specific one.
@dp.message(StateFilter(InterestingTypeHistoricalEvents.type_of_historical_event))
async def process_input_type_historical_events(message: types.Message, state: FSMContext):
    user_input = message.text
    await message.answer(f"You specified: {user_input}. Now processing your request...")
    response_historical_events = get_historical_events_for_today(user_input)
    resp_str = ''
    if response_historical_events:
        if len(response_historical_events) > 1:
            for index, hist_event in enumerate(response_historical_events):
                resp_str += f'№ {index+1}\nYEAR: {hist_event["year"]},\nMONTH: {hist_event["month"]},\nDAY: {hist_event["day"]}\n\nEVENT: {hist_event["event"]}\n\n\n'
        else:
            for hist_event in response_historical_events:
                resp_str += f'YEAR: {hist_event["year"]},\nMONTH: {hist_event["month"]},\nDAY: {hist_event["day"]}\n\nEVENT: {hist_event["event"]}\n\n\n'
    else:
        resp_str = "No historical events of the specified type for current day"

    await message.answer(resp_str)

    await state.clear()

    if response_historical_events:
        if len(response_historical_events) < 2:
            reply_markup_comment_ai = create_buttons(["I want comment from AI"])
            await message.answer("Would you like to get a comment from AI?", reply_markup=reply_markup_comment_ai)
            create_ai_comment_about_history(resp_str)

        else:
            await message.answer("Would you like to get a comment from AI? Type the number of historical event in.")
            await state.set_state(InterestingTypeHistoricalEvents.index_of_historical_event)
            await state.set_data(response_historical_events)
            logging.info('state is set InterestingTypeHistoricalEvents.index_of_historical_event')


# specific message handler.
# If making changes - not to place general message handler before specific one.

@dp.message(StateFilter(InterestingTypeHistoricalEvents.index_of_historical_event))
async def process_input_index_of_historical_event(message: types.Message, state: FSMContext):
    resp_str = ''
    historical_events = await state.get_data()
    user_input = message.text
    if not user_input.isnumeric():
        await message.answer(f"Error. You specified: {user_input}. It should be a number.")
    else:
        if int(user_input) > len(historical_events) or int(user_input) < 1:
            await message.answer(f"Error. You specified: {user_input}."
                                 f" Please type in the number of event. There are {len(historical_events)} historical events."
                                 f" Type in the number between 1 and {len(historical_events)}")
        else:
            await message.answer(f"You specified: {user_input}. Now processing your request...")

            for index, event in enumerate(historical_events):
                if (index + 1) == int(user_input):
                    resp_str = f'YEAR: {event["year"]},\nMONTH: {event["month"]},\nDAY: {event["day"]}\n\nEVENT: {event["event"]}\n\n\n'
                    ai_response = make_google_api_request('historical event, predisposing factors and historical impact', resp_str)
                    if ai_response == "Try once again later. It wasn`t possible to get necessary data" or 'It seems like AI considered your request as unappropriate..Sometimes it happens if the historical event tragic or due to some other reasons':
                        formatted_ai_response = ai_response
                    formatted_ai_response = formatting_google_ai_response_text(ai_response)
                    await message.answer(formatted_ai_response)
    reply_markup_no_input_of_number_anymore = create_buttons(['No, that`s enough'], 1)
    await message.answer(f"Would you like to get comment also about another historical event? Type in number", reply_markup=reply_markup_no_input_of_number_anymore)


@dp.callback_query(F.data == 'No, that`s enough')
async def no_more_input_number_of_historical_events(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    logging.info('state.clear() called')

def create_ai_comment_about_history(resp_str):
    @dp.callback_query(F.data == 'I want comment from AI')
    async def create_comment_from_ai_about_historical_event(callback: types.CallbackQuery):
        ai_response = make_google_api_request('historical event', resp_str)
        formatted_ai_response = formatting_google_ai_response_text(ai_response)
        await callback.message.answer(formatted_ai_response)


#All actions after pressing button 'Get morning wishes'
@dp.callback_query(F.data == 'Get morning wishes')
async def get_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    logging.info('callback is called from button with callback.data "get morning wishes"')
    choice_get_pic_reply_markup = create_buttons(["Get AI generated morning picture", "Get traditional human-created morning picture"], 1)
    await callback.message.answer("What kind of lovely morning picture would you prefer?", reply_markup=choice_get_pic_reply_markup)


@dp.callback_query(F.data == 'Get AI generated morning picture')
async def prepare_get_ai_generated_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("You have chosen to get AI generated picture.\n\nYou can type in the task for AI to create a morning picture according to your description.\n\n"
                                  "Recomendation:\nDo not ask AI to overlay text on the picture as it is a difficult job for AI and the result will be not perfect.\n\n"
                                  "After creating the picture, it will be possible to overlay text using a more traditional method.")

    await asyncio.sleep(0.5)
    reply_markup_default_instructions = create_buttons(['Use DEFAULT instructions'])

    await state.set_state(CreatingMorningWishesPic.instructions_for_AI)
    await callback.message.answer("Now you can type in the task for AI.\n\nIf you want AI to create a pleasant morning picture according to the default instructions press the button below.",
                                  reply_markup=reply_markup_default_instructions)




#specific message handler.
#If making changes - not to place general message handler before specific one.
@dp.message(StateFilter(CreatingMorningWishesPic.instructions_for_AI))
async def process_input_task_for_AI(message: types.Message, state: FSMContext):
    user_input = message.text
    await message.answer(f"You specified:\n\n{user_input}.\n\nNow processing your request...")
    await get_ai_gen_morning_wishes_pic(state, message, user_input)


@dp.callback_query(F.data=='Use DEFAULT instructions')
async def registrate_selected_font_for_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    await get_ai_gen_morning_wishes_pic(state, callback.message)

#specific message handler.
#If making changes - not to place general message handler before specific one.
@dp.message(StateFilter(CreatingMorningWishesPic.instructions_for_AI))
async def get_ai_gen_morning_wishes_pic(state: FSMContext, message: types.Message, user_input = None):

    if user_input is None:
        user_input = 'sunny early morning, nature, birds, forest, sun is shining through leaves'
        await message.answer(f'These default instructions will be applied:\n\n{user_input}')


    await state.clear()
    res_ai_generated_pic_base64_encoded = get_ai_generated_pic_for_text(user_input)
    # res_ai_generated_pic is Base64-encoded string
    if res_ai_generated_pic_base64_encoded is None:
        await message.answer(
            "Probably the limit of AI generated pictures is reached for today. Try once again tomorrow")
        return

    image_binary_data = base64.b64decode(res_ai_generated_pic_base64_encoded)
    file_name = 'generated_image.jpg'
    input_file = types.BufferedInputFile(image_binary_data, filename='generated_image.jpg')

    await state.update_data({'file_name':file_name, 'file_binary_data':image_binary_data})

    await message.answer_photo(photo=input_file)

    await message.answer('You can type in morning wishes or some other text to overlay it on the image')
    await state.set_state(CreatingMorningWishesPic.text_overlay)


#specific message handler.
#If making changes - not to place general message handler before specific one.
@dp.message(StateFilter(CreatingMorningWishesPic.text_overlay))
async def process_input_text_for_overlay_for_AI_gen_pic(message: types.Message, state: FSMContext):
    start_state = await state.get_state()

    user_input = message.text
    if user_input is not None:
        await message.answer(f"You specified: {user_input}. Now processing your request...")

        reply_markup_ask_font = create_buttons(['Default font', 'Font №1', 'Font №2', 'Font №3', 'Font №4', 'Font №5'], 3)
        await message.answer("Select the font for your text", reply_markup=reply_markup_ask_font)

        await font_selected_event.wait()
        reply_markup_ask_colour = create_buttons(['Default colour(black)', 'White', 'Red', 'Blue', 'Green', 'Yellow'],
                                               2)
        await message.answer("Select the colour for your text", reply_markup=reply_markup_ask_colour)
        font_selected_event.clear()
        await font_colour_selected_event.wait()


        font_colour_selected_event.clear()
        #state.get_data() returns {'file_name':file_name, 'file_binary_data':image_binary_data, 'font_type':font, 'font_colour':font_colour}
        received_state_data = await state.get_data()

        file_local_path = received_state_data['file_name']
        file_binary_data = received_state_data['file_binary_data']

        selected_font = received_state_data['font_type']
        selected_colour = received_state_data['font_colour']

        #input_file_binary = types.BufferedInputFile(file_binary_data, filename=file_local_path)
        with open(file_local_path, "wb") as file:
            file.write(file_binary_data)

        output_path = add_text_to_image(file_local_path, user_input, file_local_path, position=(20,30), font_size=120, font_type=selected_font, font_color=selected_colour)

        input_file = types.FSInputFile(output_path)
        await message.answer_photo(photo = input_file)

        await state.clear()

@dp.callback_query(lambda c: c.data in ['Default font', 'Font №1', 'Font №2', 'Font №3', 'Font №4', 'Font №5'])
async def registrate_selected_font_for_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    active_state = await state.get_state()
    if active_state != CreatingMorningWishesPic.text_overlay:
        await callback.message.answer('Press "Get AI generated morning picture" button to get a new picture for text overlay')
        return

    await callback.message.answer(f"You specified:\n\n{callback.data}.\n\nNow processing your request...")

    if callback.data == 'Font №1':
        font = 'Fonts/great_vibes_regular.ttf'
    elif callback.data == 'Font №2':
        font = 'Fonts/qwigley_regular.ttf'
    elif callback.data == 'Font №3':
        font = 'Fonts/ruthie_regular.ttf'
    elif callback.data == 'Font №4':
        font = 'Fonts/sibelia.ttf'
    elif callback.data == 'Font №5':
        font = 'Fonts/tangerine_regular.ttf'
    else:
        font = None

    await state.update_data({'font_type':font})
    font_selected_event.set()



@dp.callback_query(lambda c: c.data in ['Default colour(black)', 'White', 'Red', 'Blue', 'Green', 'Yellow'])
async def registrate_selected_font_color_for_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    active_state = await state.get_state()
    if active_state != CreatingMorningWishesPic.text_overlay:
        await callback.message.answer('Press "Get AI generated morning picture" button to get a new picture for text overlay')
        return
    await callback.message.answer(f"You specified:\n\n{callback.data}.\n\nNow processing your request...")
    if callback.data == 'Default colour(black)':
        font_colour = 'black'
    else:
        font_colour = callback.data.lower()

    await state.update_data({'font_colour':font_colour})
    font_colour_selected_event.set()

@dp.callback_query(F.data == 'Get traditional human-created morning picture')
async def prepare_get_traditional_morning_wishes_pic(callback: types.CallbackQuery, state: FSMContext):
    url_path_pic = get_path_morning_wishes_pic()
    input_file = types.URLInputFile(url_path_pic)
    await callback.message.answer_photo(photo=input_file)



@dp.callback_query(F.data == 'Get nature sounds')
async def prepare_get_nature_sounds(callback: types.CallbackQuery):
    parsed_audio_paths = parsed_audio_paths = [path.replace('media/nature_audio/', '').replace('.mp3', '').replace('_', " ") for path in
                          audio_paths]

    reply_markup_choice_audio = create_buttons(parsed_audio_paths,
                                             1)
    await callback.message.answer("Select audio with nature sounds", reply_markup=reply_markup_choice_audio)

    prepare_callback_answer_get_sounds(parsed_audio_paths)


def prepare_callback_answer_get_sounds(parsed_audio_paths):
    @dp.callback_query(lambda c: c.data in parsed_audio_paths)
    async def get_nature_sounds(callback: types.CallbackQuery):
        logging.info(f'callback is called from the button with callback.data: {callback.data}')
        audio_path =('media/nature_audio/'+ callback.data + '.mp3').replace(' ', '_')
        audio_file = types.FSInputFile(audio_path)
        if audio_file:
            await callback.message.answer_audio(
                audio=audio_file
            )
            return

        await callback.message.answer('No audio was found')
        logging.info('No audio was found')




#general message handler. It is located in the end because there is also specific message handler.
# If making changes - not to place general message handler before specific one.
@dp.message()
async def message_handler(message: types.Message) -> None:
    actions_options = ["Get weather conditions", "Get morning wishes", "Get today horoscope", "Get nature sounds",
                       "Get inspirational_quote", "Get historical events today"]
    logging.info(f'message.content_type: {message.content_type}')

    if message.content_type == 'location':
        actions_options_if_location_input = ["Get current weather", "Get current air quality",
                                             "Get sunset/sunrise time"]

        latitude_ = message.location.latitude
        longitude_ = message.location.longitude
        coord_dict = {'latitude': latitude_, 'longitude': longitude_}
        SESSION['Location'] = coord_dict
        reply_markup_if_location_input = create_buttons(actions_options_if_location_input, 1)

        await message.answer(
            'Thanks',
            reply_markup=reply_markup_if_location_input
        )

    text_reply = "Please, type in:\n select"
    reply_markup_ = None

    if message.text.lower() == 'select':
        reply_markup_ = create_buttons(buttons_data_list=actions_options, adjust_number=2)
        text_reply = f"Select action:"

    await message.answer(
        text_reply,
        reply_markup=reply_markup_
    )



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='w'
    )
    asyncio.run(main())

