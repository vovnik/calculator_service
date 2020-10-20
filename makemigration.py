import db.postgres as pg

from settings import *

db = pg.Postgres(dbname=DB_NAME, user=DB_USER,
                 password=DB_PASSWORD,
                 host=DB_HOST,
                 port=DB_PORT)

with open('migrations/expressiontasks.sql', 'r') as f:
    query = f.read()

with db.connect() as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()

with open('migrations/expressionresults.sql', 'r') as f:
    query = f.read()

with db.connect() as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()
