import os
import requests

# MongoDB Atlas URI
mongo_uri = "mongodb+srv://Manik:manik11@cluster0.xtzuh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Telegram bot token and chat ID
telegram_bot_token = "7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
chat_id = "-1002263879722"

def run_command(command, error_message):
    result = os.system(command)
    if result != 0:
        print(f"Error: {error_message}")
        exit(1)

def take_backup():
    # Taking backup using mongodump
    backup_command = f"mongodump --uri='{mongo_uri}' --archive=backup.gz --gzip"
    run_command(backup_command, "Failed to take MongoDB backup")
    upload_backup()

def upload_backup():
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
    with open("backup.gz", "rb") as f:
        response = requests.post(url, data={"chat_id": chat_id}, files={"document": f})
    if response.status_code == 200:
        print("Backup uploaded to Telegram successfully!")
    else:
        print("Failed to upload backup.")

# Execute the backup and upload process
take_backup()
