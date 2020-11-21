# fastapi-redis
A local cache for fastapi

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
