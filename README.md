# fastapi-redis

A local cache for fastapi.
This demo only caches for `GET` requests.
To refresh the cache, you need to trigger `/clear_cache` manually or to use `Lambda` to trigger it periodically.

Thus, the use cases this design can optimize are limited: as a service, it always gets the same `GET` request and spends quite a long time fetching data from database (or other remote services).

## How to use

1. Build fastapi-app.

```sh
docker build -t fastapi-app -f Dockerfile.fastapi .
```

2. Build postgres.

```sh
docker build -t postgres-db -f Dockerfile.postgres .
```

3. Build wait-for-it.

```sh
docker build -t wait-for-it -f Dockerfile.waitforit .
```

4. Run docker-compose.

```sh
docker-compose up
```
