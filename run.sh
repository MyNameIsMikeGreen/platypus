#!/usr/bin/env bash
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 3 platypus.wsgi
deactivate
