#!/usr/bin/env bash
source venv/bin/activate
gunicorn -w 3 --bind 0.0.0.0:8000 platypus.wsgi
deactivate
