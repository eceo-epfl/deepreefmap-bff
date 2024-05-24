FROM python:3.12.3-alpine

ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"
ENV PYTHONPATH="$PYTHONPATH:/app"

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --without dev

COPY app /app/app

ENTRYPOINT uvicorn --host=0.0.0.0 --timeout-keep-alive=0 app.main:app
