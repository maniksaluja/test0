from main import start, app
import os

# Func for purging session files.
def st():
    print("Purging session files...")
    dir = os.listdir()
    for x in dir:
        if ".session" in x or ".session-journal" in x:
            os.remove(x)

st()
print("Starting Bots...")
os.system('clear')
app.run(start())