# syntax=docker/dockerfile:1
FROM python:3.10-alpine

RUN apk update && apk add git curl gcc musl-dev libffi-dev openssl-dev

ENV POETRY_VERSION=1.7.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python - && \
    poetry --version

WORKDIR /code

RUN git clone https://github.com/Tirik8/jwt_auth_service.git .

COPY pyproject.toml ./

RUN poetry install


COPY certs/jwt-private.pem ./certs/
COPY certs/jwt-public.pem ./certs/
COPY .env .
COPY alembic.ini .
COPY ./app/core/config.py ./app/core

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]