#!/usr/bin/env bash

set -euo pipefail

PYTHON=${PYTHON:-python3}
COMMAND=${FLASK:-$PYTHON -m flask}
LC_ALL=C.UTF-8
LANG=C.UTF-8
FLASK_APP=__init__.py
if [[ "${FLASK_ENV}" == "testing" ]]; then
    $PYTHON -m "$@"
elif [[ "${FLASK_ENV}" == "production" ]]; then
    gunicorn wsgi:app --bind 0.0.0.0:5000 --access-logfile "-" --log-file "-" --preload --workers 2 --threads 2
else
    $COMMAND run "--host=0.0.0.0"
fi
