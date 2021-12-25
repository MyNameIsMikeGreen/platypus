#!/usr/bin/env bash

source venv/bin/activate

export DB_HOST=IGNORED
export DB_NAME=travis_ci_test
export DB_USER=postgres
export DB_PASSWORD=""
export DEBUG=True
export SECRET_KEY=testkey

pip install -r requirements.txt
python manage.py test --noinput
deactivate
