#!/bin/bash
export POETRY_PATH=/opt/poetry
export VENV_PATH=/opt/venv
export PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

cd /var/www/photofriends
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
poetry run $*
