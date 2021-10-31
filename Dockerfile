# syntax=docker/dockerfile:experimental

FROM python:3.9-slim as python_base

LABEL authors="benji81@gmail.com"

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    POETRY_PATH=/opt/poetry \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    VENV_PATH=/opt/venv \
    POETRY_VERSION=1.1.5

ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"


RUN apt-get update -qq && apt-get install -qq -yy libpython3-dev  ca-certificates gcc zlib1g-dev libc6-dev libjpeg-dev curl libpq-dev libmagic1 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p $POETRY_PATH $VENV_PATH /var/www /var/www/photofriends/data /var/www/photofriends/static && \
    chown -hR  www-data:www-data $POETRY_PATH $VENV_PATH /var/www/

WORKDIR /var/www/photofriends
USER www-data
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && mv /var/www/.poetry/* $POETRY_PATH/ \
    && poetry --version \
    && python -m venv $VENV_PATH \
    && poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /var/www/photofriends/
RUN poetry install --no-dev --no-interaction --no-ansi -vvv

COPY configs /var/www/photofriends/configs
COPY photofriends/ /var/www/photofriends/photofriends
COPY mainapp/ /var/www/photofriends/mainapp
COPY entrypoint.sh manage.py /var/www/photofriends/

VOLUME [ "/var/www/photofriends/static", "/var/www/photofriends/data"]

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 9000
