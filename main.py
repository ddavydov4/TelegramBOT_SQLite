import logging
import os
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlite import db_start, create_profile, edit_profile
from sqlite import get_all_users

async def on_startup(_):
    await db_start()


logging.basicConfig(level=logging.INFO)


bot_token = os.getenv('TELEGRAM_TOKEN_BOT')
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ProfileStatesGroup(StatesGroup):

    name = State()
    email = State()


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.reply('Вы прервали создание профиля, для того чтобы начать сначала напишите - /start!')


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer('Приветствую! Для того чтобы создать профиль напишите - /create')

    await create_profile(user_id=message.from_user.id)


@dp.message_handler(commands=['create'])
async def cmd_create(message: types.Message) -> None:
    await message.answer("Давайте создадим ваш профиль! Для начала отправьте своё имя! Для того чтобы прервать создание профиля напишите - /cancel")
    await ProfileStatesGroup.name.set()


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.reply('Это не имя!')


@dp.message_handler(state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer('Отлично! ' + message.text + ', пожалуйста, отправь нам свой email!')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.email)
async def check_email(message: types.Message):
    await message.reply('Это не email!')


@dp.message_handler(state=ProfileStatesGroup.email)
async def load_email(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['email'] = message.text

    await edit_profile(state, user_id=message.from_user.id)
    await message.answer('Ваш профиль успешно создан!')
    await state.finish()


@dp.message_handler(commands=['get_users'])
async def get_users(message: types.Message):
    users = await get_all_users()
    users_text = '\n'.join([f"{user['id']}. {user['name']} ({user['email']})" for user in users])
    await message.answer(users_text)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)