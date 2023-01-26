#!/usr/bin/env bash

source venv/bin/activate
pip install -r requirements.txt

echo "Making migrations..."
python3 manage.py makemigrations

echo "Flushing database..."
python3 manage.py flush --no-input

echo "Applying migrations..."
python3 manage.py migrate

echo "Populating database..."
python3 manage.py loaddata recipes.json

deactivate
