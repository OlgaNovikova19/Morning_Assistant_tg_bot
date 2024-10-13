# Morning Assistant Telegram Bot

**Morning_assistant_tg_bot** is a Telegram bot built using **aiogram 3.13.1**.

### Libraries Used:
- `asyncio`
- `requests`
- `Pillow`
- `sqlite3`
- and others.

### APIs Integrated:
The bot sends requests to the following APIs:
- **Gemini Developer API**
- **Kandinsky API**
- **API Ninjas**
- **Horoscope API**
- **API Open Meteo**

### Main Features

**Morning_assistant_tg_bot** addresses three main areas:

#### 1. Provide Practical Morning Information:
- **Current Weather Conditions**: Includes practical advice from a generative AI.
- **Air Quality Information**: Offers a detailed assessment created by generative AI.
- **Sun Data**: Provides sunrise and sunset times, daylight duration, and sunshine hours, which can be useful for planning your day.

#### 2. Provide Opportunities:
- **Nature Soundtracks**: Listen to a selection of audio tracks with nature sounds.
- **AI-Generated Morning Picture**: Create a morning-themed picture using generative AI, based on user input or default instructions for a pleasant morning image.
  - Add overlay text on the generated image using `Pillow`, with options to choose font and color, as generative AI doesn’t reliably generate graphical depictions with high-quality text overlay.

#### 3. Provide Entertainment During Your Morning Routine:
- **Horoscope Forecast**: Receive a daily horoscope, whether you know your zodiac sign or not.
- **Inspirational Quotes**: Get famous quotes, overlayed on pleasant morning pictures. The user can select the subject of the quote.
- **Historical Events**: Learn about key historical events that occurred on the current day. Optionally, a generative AI can provide comments on the factors leading to the event and its historical significance.
