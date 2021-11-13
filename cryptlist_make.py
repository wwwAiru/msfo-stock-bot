import sqlite3
import os




connct = sqlite3.connect('ms.db3')
connct.row_factory = lambda cursor, row: row[0]
curs = connct.cursor()
curs.execute('SELECT symbol FROM crypt;')
db_id = curs.fetchall()
curs.execute('SELECT name FROM crypt;')
db_id = db_id + curs.fetchall()
connct.close()

with open("cryptlist.txt", "w", encoding="utf-8") as file:
    print(*db_id, file=file, sep=", ")
