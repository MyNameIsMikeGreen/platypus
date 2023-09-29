#!/usr/bin/env bash

source initialiseVirtualEnv.sh
source read-secrets.sh

source venv/bin/activate
yum install -y postgresql-libs postgresql postgresql-devel
pip install -r requirements.txt
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
deactivate
