import datetime
import bank_currency
from config import TOKEN
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked


# logging config
logging.basicConfig(filename='bot.log', filemode='w', level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')

# Initial bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

messages_bot = []  # Bot message objects list


# Config functions start and help
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	hello = f'Привіт, <b>{message.from_user.username}</b>!👋\nЯ буду надсилати тобі актуальний курс валюти щодня. Також в мене є функція конвертації з валюти в гривні, та навпаки.'
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=hello))


# Work with exception when used blocked bot
@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception=BotBlocked):
	print(f'{exception}: {update.message.from_user.username}, id: {update.message.from_user.id}')
	return True


# Config function now (show today currency)
@dp.message_handler(commands='now')
async def currency_today(message: types.Message):
	temp = bank_currency.parse()
	content = '\n'.join([f'{i["Назва валюти"]} = {round(i["Офіційний курс"]/i["Кількість одиниць валюти"], 3)} грн' for i in temp])
	data = f'<b>Курс валют на {".".join(str(datetime.date.today()).split("-")[::-1])}</b>'
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=data))
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=content))


# Check currency for custom date
@dp.message_handler(commands='from_date')
async def get_currency_from_date(message: types.Message):
	messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text='Введіть потрібну дату у форматі ДД.ММ.РР'))
	@dp.message_handler()
	async def echo_message(message: types.Message):
		temp = bank_currency.parse()
		content = '\n'.join(
			[f'{i["Назва валюти"]} = {round(i["Офіційний курс"] / i["Кількість одиниць валюти"], 3)} грн' for i in
			 temp])
		data = f'<b>Курс валют на {message.text}</b>'
		messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=data))
		messages_bot.append(await bot.send_message(chat_id=message.from_user.id, text=content))


# Function that clean our chat (delete all the bot messages)
@dp.message_handler(commands='clear')
async def clear_chat(message: types.Message):
	for i in messages_bot:
		await bot.delete_message(message.chat.id, message_id=i.message_id)
	messages_bot.clear()


# Convert func #1
@dp.message_handler(commands='convert_to_currency')
async def convert_to_currency(message: types.Message):
	messages_bot.append(await bot.send_message(chat_id=message.chat.id, text='Введіть кількість гривень:'))
	@dp.message_handler()
	async def count_uah(message: types.Message):
		global uah
		uah = float(message.text.replace(',', '.'))
		temp = bank_currency.parse()
		keyboard = types.InlineKeyboardMarkup()
		for i in range(len(temp)):
			keyboard.add(types.InlineKeyboardButton(text=f"{temp[i]['Назва валюти']}", callback_data=f"to_{temp[i]['Код літерний']}"))
		messages_bot.append(await message.answer("В яку валюту конвертуємо:", reply_markup=keyboard))


# Call back functions (convert from uah to foreign currency)
@dp.callback_query_handler(text=[f'to_{x["Код літерний"]}' for x in bank_currency.parse()])
async def convert_uah(call: types.CallbackQuery):
	capture = call.data
	temp = bank_currency.parse()
	for i in temp:
		if i['Код літерний'] == capture.split('_')[-1]:
			messages_bot.append(await call.message.answer(f'{uah} UAH = {round(uah * i["Кількість одиниць валюти"] / i["Офіційний курс"], 2)} {i["Код літерний"].lower()}'))


# Convert func #2
@dp.message_handler(commands='convert_to_uah')
async def convert_to_uah(message: types.Message):
	messages_bot.append(await bot.send_message(chat_id=message.chat.id, text='Введіть кількість валюти:'))
	@dp.message_handler()
	async def count_values(message: types.Message):
		global value
		value = float(message.text.replace(',', '.'))
		temp = bank_currency.parse()
		keyboard = types.InlineKeyboardMarkup()
		for i in range(len(temp)):
			keyboard.add(types.InlineKeyboardButton(text=f"{temp[i]['Назва валюти']}", callback_data=f"from_{temp[i]['Код літерний']}"))
		messages_bot.append(await message.answer("З якої валюти конвертуємо:", reply_markup=keyboard))


# Call back functions (convert from foreign currency to uah)
@dp.callback_query_handler(text=[f'from_{x["Код літерний"]}' for x in bank_currency.parse()])
async def convert_currency(call: types.CallbackQuery):
	capture = call.data
	temp = bank_currency.parse()
	for i in temp:
		if i['Код літерний'] == capture.split('_')[-1]:
			messages_bot.append(await call.message.answer(f'{value} {i["Код літерний"]} = {round(value * i["Офіційний курс"] / i["Кількість одиниць валюти"], 2)} грн.'))


if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
