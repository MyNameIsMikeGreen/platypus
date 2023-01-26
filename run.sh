#!/usr/bin/env bash

source initialiseVirtualEnv.sh
source read-secrets.sh

source venv/bin/activate
pip install -r requirements.txt
python3 manage.py collectstatic --no-input
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
deactivate
