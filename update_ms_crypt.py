from requests import Request, Session
import json
import sqlite3





url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
#тут указывается лимит количества результатов(больше 5000 нельзя) для пагинации меняется параметр start
parameters = {
        'start': '1',
        'limit': '5000',
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


conn = sqlite3.connect('ms.db3')
cur = conn.cursor()
#cur.execute('DELETE FROM crypt;')
"""for x in data:
    cur.execute('''INSERT or IGNORE INTO crypt(id, name, symbol, slug, price, market_cap, volume_24h, percent_change_24h)
                         VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                (x["id"], x["name"], x["symbol"], x["slug"], x["quote"]["USD"]["price"],
                 x["quote"]["USD"]["market_cap"],
                 x["quote"]["USD"]["volume_24h"],
                 x["quote"]["USD"]["percent_change_24h"]))"""
cur.execute('DELETE FROM crypt WHERE market_cap = 0 ;')
conn.commit()
conn.close()

print("Done")

