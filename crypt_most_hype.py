import sqlite3
from update_ms_crypt_hype import update_crypt_hype



def coin_request_hype():
    update_crypt_hype()
    hype_ratio = ''
    try:
        connct = sqlite3.connect('ms.db3')
        #connct.row_factory = lambda cursor, row: row[0]
        curs = connct.cursor()
        curs.execute(f'''SELECT name, symbol, volume_24h/market_cap, price FROM crypt_hype 
        WHERE volume_24h/market_cap>=0.4 AND name!="Tether" AND name NOT LIKE "%USD%" 
        ORDER BY volume_24h/market_cap DESC
        LIMIT 10;''')
        db_result = curs.fetchall()
    except sqlite3.Error as error:
        print(error)
    finally:
        if (connct):
            connct.close()


    for i in range(len(db_result)):
        if db_result[i][3]>1:
            price_i=round(db_result[i][3],2)
        else:
            price_i=round(db_result[i][3],5)
        hype_ratio+=f'<b>{i+1}: {db_result[i][0]}</b>({db_result[i][1]})цена: <b>{(price_i)}</b>'\
                    f'\nАктивность: <b>{round(db_result[i][2],3)}</b>\n'
    return hype_ratio


