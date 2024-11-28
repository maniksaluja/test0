from main import start, app
import os

# Function for purging session files
def purge_sessions():
    print("Purging session files...")
    for filename in os.listdir():
        if filename.endswith(".session") or filename.endswith(".session-journal"):
            os.remove(filename)

# Purge session files
purge_sessions()

print("Starting Bots...")
os.system('clear')
app.run(start())
