import datetime
import bank_currency
from config import TOKEN
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
# import aiogram.utils.markdown as fmt


#logging configate
logging.basicConfig(level=logging.INFO)

#Initial bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

messages_bot = []

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	hello = f'Привіт, <b>{message.from_user.username}</b>!👋\nЯ буду надсилати тобі актуальний курс валюти щодня. Також в мене є функція конвертації з валюти в гривні, та навпаки.'
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=hello))


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception=BotBlocked):
	print(f'{exception}: {update.message.from_user.username}, id: {update.message.from_user.id}')
	return True


@dp.message_handler(commands='now')
async def currency_today(message: types.Message):
	temp = bank_currency.parse()
	content = '\n'.join([f'{i["Назва валюти"]} = {round(i["Офіційний курс"]/i["Кількість одиниць валюти"], 3)} грн' for i in temp])
	data = f'<b>Курс валют на {".".join(str(datetime.date.today()).split("-")[::-1])}</b>'
	# await message.answer(f'<b>Курс валют на {".".join(str(datetime.date.today()).split("-")[::-1])}</b>')
	# await message.answer(content)
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=data))
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=content))


@dp.message_handler(commands='clear')
async def clear_chat(message: types.Message):
	for i in messages_bot:
		await bot.delete_message(message.chat.id, message_id=i.message_id)
	messages_bot.clear()


if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)