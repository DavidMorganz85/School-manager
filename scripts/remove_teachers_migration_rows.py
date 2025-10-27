import sqlite3
import os
DB='db.sqlite3'
if not os.path.exists(DB):
    print('db not found:', DB)
    raise SystemExit(1)
conn=sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT id, app, name FROM django_migrations WHERE app='teachers'")
rows=cur.fetchall()
print('found:', rows)
cur.execute("DELETE FROM django_migrations WHERE app='teachers'")
conn.commit()
print('deleted rows count:', cur.rowcount)
cur.execute("SELECT id, app, name FROM django_migrations WHERE app='teachers'")
print('remaining:', cur.fetchall())
conn.close()
