from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import sqlite3
from thefuzz import fuzz        #подключил модули из библиотеки->
from thefuzz import process     #->fuzzywuzzy для обработки неточных соответствий




def coin_request(user_msg):
    try:
        connct = sqlite3.connect('ms.db3')
        connct.row_factory = lambda cursor, row: row[0]
        curs = connct.cursor()
        curs.execute(f'SELECT symbol FROM crypt;')
        db_str = curs.fetchall()
        connct.close()
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    #print(db_str)
    crypt_name = process.extractOne(user_msg, db_str)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    print(crypt_name)
    parameters = {
        'symbol': crypt_name[0],
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '73de3d69-c9fe-426b-859b-cfa5e9a28640',
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)['data'][crypt_name[0]]
    if data['quote']['USD']['price'] > 0:
        round_price = round(data['quote']['USD']['price'], 3)

    return f"""{data['name']} \nЦена: {round_price}
    \nСуточный объём торгов: {round(data['quote']['USD']['volume_24h'],2)} 
    \nИзменение цены за сутки {round(data['quote']['USD']['percent_change_24h'],2)}%"""

"""schedule.every(1).minutes.do(coin_request)
while True:
    schedule.run_pending()
    time.sleep(1)"""
