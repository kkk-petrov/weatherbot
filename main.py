import pyowm
from config import API_TOKEN, OWM_TOKEN
from aiogram.types import ContentTypes
from pyowm.utils.config import get_default_config
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import emoji




class CityName(StatesGroup):
    city_name = State()
    city_name2 = State()


# ============================= BOT =============================
# Уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Русская локализация pyowm
config_dict = get_default_config()
config_dict['language'] = 'ru'

# Инициализация pyowm
owm = pyowm.OWM(OWM_TOKEN, config_dict)
mgr = owm.weather_manager()


# Обработка команд
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я бот-синоптик" + emoji.emojize(':sun_with_face:')
                        + "\nНапиши /help что-бы узнать мои возможности " + emoji.emojize(':exploding_head:') + "!")

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("Список моих возможностей:\n" + emoji.emojize(':umbrella:')
                         + "/weather - узнать краткую информацию о погоде на сегодня\n"
                         + emoji.emojize(':rainbow:') + "/detweather - узнать детальную информацию о погоде на сегодня\n")



@dp.message_handler(commands=['weather'], state=None)
async def send_question(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Каховка")
    keyboard.add(button)
    await message.answer(emoji.emojize(':balloon:') + "О каком городе вы хотите узнать информацию?"
                         + emoji.emojize(':house:'), reply_markup=keyboard)
    await CityName.city_name.set()


@dp.message_handler(state=CityName.city_name)
async def answer_city(message: types.Message, state: FSMContext):
    await message.reply(emoji.emojize(":globe_with_meridians:Секунду..."), reply_markup=types.ReplyKeyboardRemove())

    cityName = message.text
    await state.update_data(city=cityName)

    try:
        observation = mgr.weather_at_place(cityName)
        w = observation.weather
        t = w.temperature('celsius')
        temp = t['feels_like']

        wt = (emoji.emojize(':pushpin:') + "В городе " + cityName.title() + " сейчас " + w.detailed_status
              + emoji.emojize(':eyes:') + "\n\n")
        wt += (emoji.emojize(':thermometer:') + "Температура в районе " + str(temp) + "°C" + "\n\n")

        if temp < 10:
            wt += (emoji.emojize(':radio_button:') + "На улице довольно холодно, одевайся потеплее!"
                   + emoji.emojize(':snowflake:'))
        elif temp < 20 and temp > 10:
            wt += (emoji.emojize(':radio_button:') + "На улице прохладно, накинь куртку хотя-бы!"
                   + emoji.emojize(':umbrella:'))
        elif temp > 20:
            wt += (emoji.emojize(':radio_button:') + "На улице тепло, одевай что-угодно!"
                   + emoji.emojize(':sun:'))

        await message.answer(wt)
        await state.finish()
    except:
        await message.reply(emoji.emojize(':globe_with_meridians:') + "Пожалуйста, введите корректное название города!"
                            + emoji.emojize(':warning:'))


@dp.message_handler(commands=['detweather'], state=None)
async def send_question2(message: types.Message):
#   Клавиатура Каховка
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Каховка")
    keyboard.add(button)
    await message.answer(emoji.emojize(':balloon:') + "О каком городе вы хотите узнать информацию?"
                         + emoji.emojize(':house:'), reply_markup=keyboard)
    await CityName.city_name2.set()


@dp.message_handler(state=CityName.city_name2)
async def answer_city2(message: types.Message, state: FSMContext):
    await message.reply(emoji.emojize(":globe_with_meridians:Секунду..."), reply_markup=types.ReplyKeyboardRemove())
    cityName = message.text
    await state.update_data(city=cityName)

    try:
        observation = mgr.weather_at_place(cityName)
        w = observation.weather
        t = w.temperature('celsius')
        temp = t['feels_like']
        temp_min_info = t['temp_min']
        temp_max_info = t['temp_max']
        wind_info = w.wind()['speed']

        dwt = (emoji.emojize(':pushpin:') + "В городе " + cityName.title() + " сейчас " + w.detailed_status
               + emoji.emojize(':eyes:') + "\n\n")
        dwt += (emoji.emojize(':cyclone:') + "Скорость ветра - " + str(wind_info) + " м/с.\n\n")
        dwt += (emoji.emojize(':thermometer:') + "Минимальная температура: " + str(temp_min_info) + "°C.\n")
        dwt += (emoji.emojize(':thermometer:') + "Максимальная температура: " + str(temp_max_info) + "°C." + "\n")
        dwt += (emoji.emojize(':thermometer:') + "Ощущается как " + str(temp) + "°C.\n\n\n")

        if temp < 10:
            dwt += (emoji.emojize(':radio_button:') + "На улице довольно холодно, одевайся потеплее!"
                    + emoji.emojize(':snowflake:'))
        elif temp < 20 and temp > 10:
            dwt += (emoji.emojize(':radio_button:') + "На улице прохладно, лучше накинь куртку!"
                    + emoji.emojize(':umbrella:'))
        elif temp > 20:
            dwt += (emoji.emojize(':radio_button:') + "На улице тепло, одевай что-угодно!"
                    + emoji.emojize(':sun:'))

        await message.answer(dwt)
        await state.finish()
    except:
        await message.reply(emoji.emojize(':globe_with_meridians:') + "Пожалуйста, введите корректное название города!"
                            + emoji.emojize(':warning:'))


# Хэндлеры для неожиданных ботом сообщений
@dp.message_handler()
async def echo_message(msg: types.Message):
    reminder = emoji.emojize('Я не знаю, что с этим делать :face_with_monocle:\nЯ просто напомню, что есть команда /help :call_me_hand:')
    await bot.send_message(msg.from_user.id, msg.text)
    await msg.reply(reminder)

@dp.message_handler(content_types=ContentTypes.ANY)
async def unknown_message(msg: types.Message):
    reminder = emoji.emojize('Я не знаю, что с этим делать :face_with_monocle:\nЯ просто напомню, что есть команда /help :call_me_hand:')
    await msg.reply(reminder)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
