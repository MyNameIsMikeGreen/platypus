#!/usr/bin/env bash

gunicorn -w 3 -b 0.0.0.0:8000 platypus.wsgi
