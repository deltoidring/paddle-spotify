FROM python:3.11.4-alpine3.17 as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

FROM python-base as builder

ENV PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.1 \
  POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main

FROM python-base as app
ENV PYTHONPATH="/app:/app/.venv/:$PYTHONPATH"
WORKDIR /src
COPY --from=builder /app/.venv /app/.venv
COPY ./paddle /app/paddle/
ENTRYPOINT ["python", "-m"]
