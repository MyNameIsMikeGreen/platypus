import psycopg2
import os

DATABASE_CONNECTION = psycopg2.connect(host=os.environ["DB_HOST"],
                                       database=os.environ["DB_NAME"],
                                       user=os.environ["DB_USER"],
                                       password=os.environ["DB_PASSWORD"]
                                       )


def app(environ, start_response):
    cur = DATABASE_CONNECTION.cursor()
    cur.execute('SELECT version()')
    db_version = cur.fetchone()[0]
    cur.close()
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(db_version)))
    ])
    return iter([str.encode(db_version)])
