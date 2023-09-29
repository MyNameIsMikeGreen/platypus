#!/usr/bin/env bash

source initialiseVirtualEnv.sh
source read-secrets.sh

source venv/bin/activate
pip install psycopg2-binary~=2.9.3
export PATH="$HOME/.local/bin:$PATH"
pip install -r requirements.txt
gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
deactivate
