#!/usr/bin/env bash

pip install --upgrade pip
set -o errexit  # exit on error

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate