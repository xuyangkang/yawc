# Yet another website crawler

## Purposal
To crawl(more exactly to download) a large collections of websites.

## Design
TBD

## Setup

Create DB and fetch_status table in AWS.

```
CREATE TABLE fetch_status(
   id serial PRIMARY KEY,
   filename VARCHAR (50) NOT NULL,
   status VARCHAR (50) NOT NULL,
   last_update TIMESTAMP NOT NULL
);
```

## Envs
```
DB_HOST
DB_PORT
DB_USER
DB_NAME
DB_PASSWORD
```

## TODO
```python
# TODO: update crawl status in db
import psycopg2
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_USER = os.getenv('DB_USER', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'yawc')
DB_PASSWORD = os.getenv('DB_PASSWORD')

conn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

cur = conn.cursor()

cur.execute('SELECT version()')

db_version = cur.fetchone()
print(db_version)

cur.close()
conn.close()
```
