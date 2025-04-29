FROM python:3.10. AS builder

RUN python -m pip install --no-cache-dir poetry==1.4.2 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY . ./app 

WORKDIR /app

RUN ["poetry", "install"]

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]