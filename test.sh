#!/usr/bin/env bash

source setup.sh
source read-secrets.sh

source venv/bin/activate
pip install -r requirements.txt
python manage.py test --noinput
deactivate
