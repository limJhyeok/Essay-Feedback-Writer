#! /usr/bin/env sh
set -e

if [ -f /app/app/main.py ]; then
    DEFAULT_MODULE_NAME=app.main
elif [ -f /app/main.py ]; then
    DEFAULT_MODULE_NAME=main
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}


LOG_LEVEL=${LOG_LEVEL:-info}

# If there's a prestart.sh script in the /app directory, run it before starting
PRE_START_PATH=/app/scripts/prestart.sh
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

alembic upgrade head

# Start Uvicorn with live reload
exec uvicorn --reload --host 0.0.0.0 --port 8000 --log-level $LOG_LEVEL "$APP_MODULE"
