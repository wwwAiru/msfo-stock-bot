from requests import Request, Session
import json
import sqlite3




def update_crypt_hype():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    #тут указывается лимит количества результатов(больше 5000 нельзя) для пагинации меняется параметр start
    parameters = {
            'start': '1',
            'limit': '200',
            'convert': 'USD'
    }
    headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '02925efd-b47c-4000-a468-5078c3ed6c9b',
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)['data']

    try:
        conn = sqlite3.connect('ms.db3')
        cur = conn.cursor()
        cur.execute('DELETE FROM crypt_hype;')
        for x in data:
            cur.execute('''INSERT or IGNORE INTO crypt_hype(id, name, symbol, price, market_cap, volume_24h, percent_change_24h)
                             VALUES(?, ?, ?, ?, ?, ?, ?)''',
                    (x["id"], x["name"], x["symbol"], x["quote"]["USD"]["price"],
                     x["quote"]["USD"]["market_cap"],
                     x["quote"]["USD"]["volume_24h"],
                     x["quote"]["USD"]["percent_change_24h"]))
        cur.execute('DELETE FROM crypt_hype WHERE market_cap = 0;')
        conn.commit()
    except sqlite3.Error as error:
        print(err)
    finally:
        if (conn):
            conn.close()
    print("Таблица crypt_hype обновлена.")

