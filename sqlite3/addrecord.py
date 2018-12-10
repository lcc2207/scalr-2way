import sqlite3

conn = sqlite3.connect('/opt/sqlite/db')
c = conn.cursor()


c.execute("insert into approval_table values('b7f5edcf-88fb-4a87-96e4-f56871bcaad7','pending');")

conn.commit()
conn.close()
