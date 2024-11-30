#!/bin/bash

# Kill existing screen session
pkill -f manik_session

# Pull latest code
git pull
clear

# Create virtual environment if not exists
if [ ! -d "manik" ]; then
    python3 -m venv manik
fi

# Activate virtual environment
source manik/bin/activate
clear

# Start screen session and run start.py
screen -dmS manik_session
screen -S manik_session -X stuff 'python3 start.py\n'
