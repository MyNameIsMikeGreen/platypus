#!/usr/bin/env sh

source read-secrets.sh

pip install -r requirements.txt
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
