from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import sqlite3
from thefuzz import fuzz        #подключил модули из библиотеки->
from thefuzz import process     #->fuzzywuzzy для обработки неточных соответствий
import os
from decimal import Decimal, getcontext



#открываем файл
with open('cryptlist.txt', 'r', encoding="utf-8") as f:
    crypt_file = f.read()
#преобразуем файл в список
crypt_list = crypt_file.split(', ')
#устанавливаем контекст преобразования для Decimal в 15 знаков
getcontext().prec = 15

def coin_request(user_msg):
    #сравниваем пользовательский месадж со списком
    corrected_query = process.extractOne(user_msg, crypt_list)
    print(corrected_query)
    #получаем кортеж с самым совпадающим значением и процентом совпадения
    #используем для запроса в бд чтобы получиь id
    try:
        connct = sqlite3.connect('ms.db3')
        connct.row_factory = lambda cursor, row: row[0]
        curs = connct.cursor()
        # запрос по имени крипты, после правки возможной неточности или ошибки пользовательского ввода
        curs.execute(f'SELECT id FROM crypt WHERE symbol="{corrected_query[0]}" OR name="{corrected_query[0]}";')
        db_id = curs.fetchone()
    except sqlite3.Error as error:
        print(error)
    finally:
        if (connct):
            connct.close()
    print(db_id)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'id': db_id,
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '73de3d69-c9fe-426b-859b-cfa5e9a28640',
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)['data'][str(db_id)]
    number = Decimal(data['quote']['USD']['price'])
    if number < 0.000001:
        retrr = number.quantize(Decimal("0.000000000001"))
    elif number < 0.01:
        retrr = number.quantize(Decimal("0.00000001"))
    elif number < 0.5:
        retrr = number.quantize(Decimal("0.0001"))
    else:
        retrr = number.quantize(Decimal("0.01"))

#делаем человекочитаемый вывод данных. в суточный объём торгов добавил разделитель-запятую т.к. числа большие
    return f"""{data['name']} ({data['symbol']}) Цена: {retrr}$
    \nКапитализация: {round(data['quote']['USD']['market_cap']):,}$
    \nСуточный объём торгов: {round(data['quote']['USD']['volume_24h']):,}$
    \nИзменение цены за сутки: {round(data['quote']['USD']['percent_change_24h'],2)}%"""


