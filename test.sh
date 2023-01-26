#!/usr/bin/env bash

source initialiseVirtualEnv.sh
source venv/bin/activate

export DB_HOST=test.mynameismikegreen.co.uk
export DB_NAME=./platypus.db.test

pip install -r requirements.txt
python manage.py test --noinput
deactivate
