import os
import requests

# Telegram bot token and chat ID
telegram_bot_token = "7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
chat_id = "-1002263879722"

def run_command(command, error_message):
    result = os.system(command)
    if result != 0:
        print(f"Error: {error_message}")
        exit(1)

def take_backup():
    os.system("mongodump --archive=backup.tar.gz --gzip")
    upload_backup()

def upload_backup():
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
    with open("backup.tar.gz", "rb") as f:
        response = requests.post(url, data={"chat_id": chat_id}, files={"document": f})
    if response.status_code == 200:
        print("Backup uploaded to Telegram successfully!")
    else:
        print("Failed to upload backup.")

# Create MongoDB user if not already created
mongo_commands = """
mongosh <<EOF
use myNewDatabase
if (db.getUser('manik') == null) {
  db.createUser({
    user: "manik",
    pwd: "manik",
    roles: [{ role: "readWrite", db: "myNewDatabase" }]
  })
} else {
  print("User 'manik' already exists.")
}
EOF
"""
run_command(mongo_commands, "Failed to create MongoDB user")

# Backup Verification and Restoration
def check_telegram_backup():
    url = f"https://api.telegram.org/bot{telegram_bot_token}/getUpdates"
    response = requests.get(url).json()
    
    for update in response["result"]:
        if "message" in update and "document" in update["message"]:
            if "backup" in update["message"]["document"]["file_name"]:
                file_id = update["message"]["document"]["file_id"]
                file_path = get_file_path(file_id)
                download_backup(file_path)
                return True
    return False

def get_file_path(file_id):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/getFile?file_id={file_id}"
    response = requests.get(url).json()
    return response["result"]["file_path"]

def download_backup(file_path):
    download_url = f"https://api.telegram.org/file/bot{telegram_bot_token}/{file_path}"
    response = requests.get(download_url)
    with open("backup.tar.gz", "wb") as f:
        f.write(response.content)
    os.system("tar -xzvf backup.tar.gz -C /var/lib/mongodb")
    print("Backup restored successfully!")

# Check for backup in Telegram
if not check_telegram_backup():
    print("No backup found. Creating new database.")
    take_backup()
else:
    print("Backup found and restored.")

# Schedule Backup
take_backup()

Es se kya kya hoga 
