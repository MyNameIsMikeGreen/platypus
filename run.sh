#!/usr/bin/env bash

export PATH="$HOME/.local/bin:$PATH"
source initialiseVirtualEnv.sh
source read-secrets.sh

source venv/bin/activate
pip install psycopg2-binary~=2.9.3
pip install -r requirements.txt
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
deactivate
