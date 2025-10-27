import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT app, name, applied FROM django_migrations WHERE app='classes' ORDER BY applied")
rows = cur.fetchall()
print('django_migrations entries for classes:')
for r in rows:
    print(r)

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'classes_%' ORDER BY name")
print('\nclasses_ tables:')
for r in cur.fetchall():
    print(r[0])

conn.close()
