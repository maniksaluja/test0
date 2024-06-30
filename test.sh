
git pull
clear

if [ ! -d "manik" ]; then
    python3 -m venv manik
fi

source manik/bin/activate
clear
python3 start.py
