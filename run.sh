#!/usr/bin/env bash
source venv/bin/activate
gunicorn -w 3 platypus.wsgi
deactivate
