#!/bin/sh

sleep 10

python manage.py makemigrations
python manage.py migrate

exec "$@"