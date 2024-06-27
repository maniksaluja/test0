from main import start, app
import os

# Func for purging session files.
def st():
    os.system("git pull")
    os.system("clear")
    if not "manik" in os.listdir():
        os.system("python3 -m venv manik")
    os.system("source manik/bin/activate")
    os.system("clear")
    os.system("screen")
    print("Purging session files...")
    dir = os.listdir()
    for x in dir:
        if ".session" in x or ".session-journal" in x:
            os.remove(x)

st()
print("Starting Bots...")
os.system('clear')
app.run(start())