import os
from typing import Optional

import psycopg2
import redis
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
cache = redis.Redis(host='redis', port=6379)
conn = psycopg2.connect(database=os.environ.get("POSTGRES_DB"),
                        user=os.environ.get("POSTGRES_USER"),
                        password=os.environ.get("POSTGRES_PASSWORD"),
                        host="db",
                        port="5432")

@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.get("/cache")
def read_root():
    count = get_hit_count()
    return {"cache_hit": count}


def get_value_by_key_from_db(key: str):
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM key_values WHERE key=%s", (key,))
    rows = cur.fetchall()

    value = None
    for row in rows:
        key = row[0]
        value = row[1]
    return value


@app.get("/key_values/{key}")
def get_key_value(key: str):
    value = get_value_by_key_from_db(key)
    return {"key": key, "value": value}


class KeyValue(BaseModel):
    key: str
    value: str


def set_value_by_key_to_db(key: str, value: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO key_values (key,value) VALUES (%s,%s)", (key, value))
    conn.commit()


@app.post("/key_values")
def set_key_value(kv: KeyValue):
    set_value_by_key_to_db(kv.key, kv.value)
    return kv


def update_value_by_key_to_db(key: str, value: str):
    cur = conn.cursor()
    cur.execute("UPDATE key_values SET value=%s WHERE key=%s", (value, key))
    conn.commit()


@app.patch("/key_values/{key}")
def update_value_by_key(key: str, kv: KeyValue):
    update_value_by_key_to_db(key, kv.value)
    return kv
