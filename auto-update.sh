#!/bin/bash

APP_DIR="$HOME/edu-search/lf-app/app"
LOG_FILE="$APP_DIR/update.log"
GUNICORN_PID_FILE="$APP_DIR/gunicorn.pid"
GUNICORN_CMD="gunicorn -w 2 -b 0.0.0.0:8000 app:app --pid $GUNICORN_PID_FILE"

cd "$APP_DIR" || exit

# Fetch latest commits
git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "$(date): New version detected. Updating..." >> "$LOG_FILE"

    git pull origin main >> "$LOG_FILE" 2>&1

    # Install new dependencies (assumes pip is user-local)
    pip install --user -r requirements.txt >> "$LOG_FILE" 2>&1

    # Restart gunicorn
    if [ -f "$GUNICORN_PID_FILE" ]; then
        kill -HUP "$(cat $GUNICORN_PID_FILE)"
        echo "$(date): Gunicorn restarted (HUP)." >> "$LOG_FILE"
    else
        echo "$(date): Starting Gunicorn..." >> "$LOG_FILE"
        nohup $GUNICORN_CMD >> "$APP_DIR/gunicorn.log" 2>&1 &
    fi
else
    echo "$(date): No update needed." >> "$LOG_FILE"
fi
