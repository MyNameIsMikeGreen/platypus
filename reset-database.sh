#!/usr/bin/env sh

source read-secrets.sh

pip install -r requirements.txt

echo "Making migrations..."
python manage.py makemigrations

echo "Flushing database..."
python manage.py flush --no-input

echo "Applying migrations..."
python manage.py migrate

echo "Populating database..."
python manage.py loaddata recipes.json
