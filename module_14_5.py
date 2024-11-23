from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

api = '7837548987:AAFTQ6z7_o3tgIzEELQEiBSEwLPRlpHTNBw'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Рассчитать')],
    [KeyboardButton(text="Информация")],
    [KeyboardButton(text="Купить")],
    [KeyboardButton(text='Регистрация')],
]
    , resize_keyboard=True)

kb2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')],
        [InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ])

kb3 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Product1", callback_data="product_buying")],
                     [InlineKeyboardButton(text="Product2", callback_data="product_buying")],
                     [InlineKeyboardButton(text="Product3", callback_data="product_buying")],
                     [InlineKeyboardButton(text="Product4", callback_data="product_buying")]
                     ])


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()



all_products = get_all_products()


@dp.message_handler(commands='start')
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if is_included(username):
        await message.answer('Пользователь существует, введите другое имя')
    else:
        await state.update_data(username=username)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age= message.text)
    get = await state.get_data()
    username = get['username']
    email = get['email']
    age = get['age']
    add_user(username, email, age)
    await message.answer('Регистрация прошла успешно')
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    num = 0
    for product in all_products:
        num += 1
        await message.answer(f'Название: {product[0]} | Описание: {product[1]} | Цена: {product[2]}')
        with open(f"{num}.jpg", 'rb') as img:
            await message.answer_photo(img)
    await message.answer("Выберите продукт для покупки:", reply_markup=kb3)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def send_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    weight = int(data['weight'])
    growth = int(data['growth'])
    stndrt = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f"Ваша норма калорий {stndrt}")
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)