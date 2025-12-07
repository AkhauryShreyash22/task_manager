#!/bin/sh

echo "Running Django migrations..."
python tasks/manage.py migrate

echo "Starting Django..."
exec "$@"
