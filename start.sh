#!/bin/bash
set -e

echo "Starting Navi..."
echo "================"

# Check environment
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and fill in your keys."
    exit 1
fi

# Init database
python3 -c "import db; db.init_db(); print('Database ready')"

# Start bot (includes dashboard + cron scheduler)
python3 bot.py
