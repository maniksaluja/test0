#!/bin/bash

pkill screen
git pull
clear

if [ ! -d "manik" ]; then
    python3 -m venv manik
fi

source manik/bin/activate
clear

screen -q
python3 start.py