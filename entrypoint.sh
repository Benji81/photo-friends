#!/bin/bash
export POETRY_PATH=/opt/poetry
export VENV_PATH=/opt/venv
export PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

cd /var/www/photofriends
if [ $INIT == "1" ]; then
  poetry run python manage.py migrate
  poetry run python manage.py collectstatic --noinput
fi
poetry run $*
