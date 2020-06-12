import psycopg2
import os

DATABASE_CONNECTION = psycopg2.connect(host=os.environ["DB_HOST"],
                                       database=os.environ["DB_NAME"],
                                       user=os.environ["DB_USER"],
                                       password=os.environ["DB_PASSWORD"]
                                       )


def app(environ, start_response):
    cur = DATABASE_CONNECTION.cursor()
    cur.execute('SELECT title, method FROM recipes')
    record = cur.fetchone()
    cur.close()
    response_body = record[0] + "\n\n" + record[1]
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(response_body)))
    ])
    return iter([str.encode(response_body)])
