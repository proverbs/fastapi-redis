import os
from typing import Any, Mapping, List

import psycopg2
import redis
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()
cache = redis.StrictRedis(host='redis',
                          port=6379,
                          charset="utf-8",
                          decode_responses=True)
conn = psycopg2.connect(database=os.environ.get("POSTGRES_DB"),
                        user=os.environ.get("POSTGRES_USER"),
                        password=os.environ.get("POSTGRES_PASSWORD"),
                        host="db",
                        port="5432")
conn.set_client_encoding('UTF8')


@app.get("/")
def read_root() -> Mapping[str, Any]:
    return {"Hello": "World"}


def get_value_by_key_from_db(key: str) -> str:
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM key_values WHERE key=%s", (key, ))
    rows = cur.fetchall()

    value = None
    for row in rows:
        key = row[0]
        value = row[1]
    return value


@app.get("/key_values/{key}")
def get_key_value(key: str) -> Mapping[str, Any]:
    value = cache.get(key)
    if not value:
        value = get_value_by_key_from_db(key)

    if value:
        cache.set(key, value)

    return {"key": key, "value": value}


class KeyValue(BaseModel):
    key: str
    value: str


def set_value_by_key_to_db(key: str, value: str) -> None:
    cur = conn.cursor()
    cur.execute("INSERT INTO key_values (key,value) VALUES (%s,%s)",
                (key, value))
    conn.commit()


@app.post("/key_values")
def set_key_value(kv: KeyValue) -> KeyValue:
    set_value_by_key_to_db(kv.key, kv.value)
    return kv


def update_value_by_key_to_db(key: str, value: str) -> None:
    cur = conn.cursor()
    cur.execute("UPDATE key_values SET value=%s WHERE key=%s", (value, key))
    conn.commit()


@app.patch("/key_values/{key}")
def update_value_by_key(key: str, kv: KeyValue) -> KeyValue:
    update_value_by_key_to_db(key, kv.value)
    return kv


def update_all_key_values_in_cache() -> List[str]:
    # Updating all the cache usually take a long time, so I just want to use
    # sleep to simulate a long task here.
    import time
    time.sleep(5)

    keys = list(cache.scan_iter())
    for key in keys:
        value = get_value_by_key_from_db(key)
        if not value:
            cache.delete(key)
        else:
            cache.set(key, value)
    return keys


@app.post("/clear_cache")
def clear_cache() -> Mapping[str, Any]:
    count = 0
    keys = list(cache.scan_iter())
    for key in keys:
        cache.delete(key)
        count += 1
    return {"count": count, "keys": keys}


@app.post("/async_update_cache")
async def async_update_cache(
        background_tasks: BackgroundTasks) -> Mapping[str, Any]:
    background_tasks.add_task(update_all_key_values_in_cache)
    return {"status": "updating cache in the background..."}


@app.post("/update_cache")
def update_cache() -> Mapping[str, Any]:
    keys = update_all_key_values_in_cache()
    return {"count": len(keys), "keys": keys}
