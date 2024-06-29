#!/bin/bash

pkill screen
git pull
clear

if [ ! -d "manik" ]; then
    python3 -m venv manik
fi

source manik/bin/activate
clear

screen -dmS manik_session
screen -S manik_session -X stuff 'python3 start.py\n'