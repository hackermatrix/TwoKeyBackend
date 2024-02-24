#!/bin/bash
python manage.py collectstatic --no-input

python manage.py migrate --fake

# python -c "while(True):i=1"
python manage.py runserver 0.0.0.0:8000
# gunicorn backend.wsgi:application --bind localhost:8000 
