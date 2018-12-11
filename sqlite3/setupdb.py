import sqlite3

conn = sqlite3.connect('/opt/sqlite/db')
c = conn.cursor()

c.execute('create table approval_table(id varchar(30), farmname varchar(30), owner_email varchar(30), operation varchar(30), status varchar(30));')
c.execute('CREATE UNIQUE INDEX indexname ON approval_table(id);')

conn.commit()
conn.close()
