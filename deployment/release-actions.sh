#!/usr/bin/env bash

# These actions are intended to be run during the Heroku release phase.
# The script should not be run manually
python manage.py makemigrations
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata recipes.json
