import sqlite3


baze=sqlite3.connect('app.db')




cursor1 = baze.cursor()

query1 = 'SELECT * FROM Receipt'


cursor1.execute(query1)
for i in cursor1:
    print(i)




