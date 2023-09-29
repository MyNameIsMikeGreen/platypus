#!/usr/bin/env bash

source initialiseVirtualEnv.sh
source read-secrets.sh

source venv/bin/activate
yum install postgresql-libs
pip install -r requirements.txt
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
deactivate
