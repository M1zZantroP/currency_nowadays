import requests
from bs4 import BeautifulSoup
import lxml
import csv


URL = 'https://bank.gov.ua/ua/markets/exchangerates?&period=daily'


def get_html(url):
	r = requests.get(URL).text
	return r


def get_currency_values(html):
	soup = BeautifulSoup(html, 'lxml')
	items = soup.find_all('tr')
	temp = []
	for i in items[1:]:
		temp.append({
			'Код цифровий': i.find('td').get_text(strip=True),
			'Код літерний': i.find('td').find_next('td').get_text(strip=True),
			'Кількість одиниць валюти': int(i.find('td').find_next('td').find_next('td').get_text(strip=True)),
			'Назва валюти': i.find('a').get_text(strip=True),
			'Офіційний курс': float(i.find('a').find_next('td').get_text(strip=True).replace(',', '.'))
		})
	return temp


def parse():
	html = get_html(URL)
	values = get_currency_values(html)
	# with open('zzz.csv', 'w') as file:
	# 	writer = csv.DictWriter(file, fieldnames=[x for x in values[0].keys()])
	# 	writer.writeheader()
	#
	# 	for i in values:
	# 		writer.writerow(i)
	return values
