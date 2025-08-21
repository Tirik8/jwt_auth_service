# syntax=docker/dockerfile:1
FROM python:3.10-alpine

RUN apk update && apk add curl gcc musl-dev libffi-dev openssl-dev

ENV POETRY_VERSION=1.7.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python - && \
    poetry --version

WORKDIR /code

COPY app/* ./app
COPY main.py .  

COPY pyproject.toml ./

RUN poetry install


COPY certs/jwt-private.pem ./certs/
COPY certs/jwt-public.pem ./certs/
COPY .env .
COPY alembic.ini .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]