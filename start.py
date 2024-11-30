import os
from main import start, app

# Function for purging session files
def purge_sessions():
    print("Purging session files...")
    for filename in os.listdir():
        if filename.endswith(".session") or filename.endswith(".session-journal"):
            try:
                os.remove(filename)
                print(f"Removed: {filename}")
            except Exception as e:
                print(f"Error removing {filename}: {e}")

# Purge session files
purge_sessions()

print("Starting Bots...")
os.system('clear' if os.name != 'nt' else 'cls')  # Clear screen command for Windows
app.run(start())
