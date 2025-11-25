FROM python:3.13-slim AS mgfn-weather

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/var/www/mgfn-weather

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

COPY ../../../pyproject.toml /usr/var/www/mgfn-weather

RUN uv sync

COPY ../../../ /usr/var/www/mgfn-weather

RUN chmod +x /usr/var/www/mgfn-weather/src/tests/infra/entrypoint.sh

CMD ["/usr/var/www/mgfn-weather/src/tests/infra/entrypoint.sh"]
