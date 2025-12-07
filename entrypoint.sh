#!/bin/sh

echo "Running Django migrations..."
python manage.py migrate

echo "Starting Django..."
exec "$@"
