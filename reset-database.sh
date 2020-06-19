#!/usr/bin/env bash
source venv/bin/activate

echo "Making migrations..."
python manage.py makemigrations

echo "Flushing database..."
python manage.py flush --no-input

echo "Applying migrations..."
python manage.py migrate

echo "Populating database..."
python manage.py loaddata recipes.json

deactivate
