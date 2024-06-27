#!/bin/bash

pkill screen
git pull
clear

if [ ! -d "manik" ]; then
    python3 -m venv manik
fi

source manik/bin/activate
clear

expect -c "
spawn screen
send \"\r\"
expect eof
"

python3 start.py
