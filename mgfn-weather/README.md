# MGFN weather
Service, that is responsible for the weather info processing.

## URL info:
* host: `0.0.0.0`
* port: `5000`
* swagger URL:
     - Using the application without nginx: `0.0.0.0:5000/api/weather/swagger`
     - Behind nginx: `0.0.0.0/api/weather/swagger`

## Common steps:
1. Add `.env` file to root (see [env variables sample](.env.sample)):

| Env Variable                               | Default Value      | Required | Description                                                    |
|--------------------------------------------|--------------------|----------|----------------------------------------------------------------|
| `POSTGRES_SERVER`                          | ❌                 | ✅       |Postgres address (host:port)                                    |
| `POSTGRES_USER`                            | ❌                 | ✅       |Postgres user                                                   |
| `POSTGRES_PASSWORD`                        | ❌                 | ✅       |Postgres user's password                                        |
| `POSTGRES_DB`                              | ❌                 | ✅       |Postgres database's name                                        |
| `WEATHER_PROVIDER_API_KEY`                 | ❌                 | ✅       |API Key for the weather provider requests                       |
| `MINIO_ADDRESS`                            | ❌                 | ✅       |Minio storage address (host:port)                               |
| `MINIO_ACCESS_KEY`                         | ❌                 | ✅       |Minio user (equals to `MINIO_ROOT_USER` env set in minio instance)|
| `MINIO_SECRET_KEY`                         | ❌                 | ✅       |Minio user's password (equals to `MINIO_ROOT_PASSWORD` env set in minio instance)|
| `MINIO_BUCKET`                             | `weather`          | ❌       |Minio bucket's name for this service                            |
| `DEBUG`                                    | `False`            | ❌       |Turns on/off debug mode                                         |

## Dev mode
### In case you want to run the application locally, do the following:
1. Make sure you have `uv` installed. If you don't, follow the instructions: https://docs.astral.sh/uv/getting-started/installation/#installation-methods.
2. If you don't have required python version (described in pyproject.toml) installed on your PC, install it by executing the command: `uv python install <python version's number>`.
3. Execute the following commands in terminal:
    * Preparation (do it only once):
        * uv sync
        * source .venv/bin/activate
        * chmod +x entrypoint.sh
    * To run the service:
        * ./entrypoint.sh


## Developer instructions:
1. To add new library use `uv add <library name>`, then `uv sync`;

### For using pre-commit webhooks it's necessary to:
1. Add webhook config to git `git add .pre-commit-config.yaml`
2. Initialize pre-commit `pre-commit install`

After that code formatter will be run before every commit and if code changes don't match with code style it will reformat code automatically. After that you should `add` and `commit` changes again. **To prevent this** "double committing" just run `ruff --fix .` before every commit by yourselves.


### Weather provider
[Yandex Weather API documentation](https://yandex.ru/dev/weather/doc/ru/concepts/forecast-rest#forecasts)

### Geodecoder
[Openstreetmap](https://nominatim.openstreetmap.org) is used as geodecoder. It's URL is not in envs but hardcoded, cuz anyway it would be neccessary to change the code if you decide to change geodecoder.
