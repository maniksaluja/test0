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

def is_installed(package_name):
    result = os.system(f"dpkg -s {package_name} &> /dev/null")
    return result == 0

# Step 1: Install MongoDB dependencies
print("Checking and installing MongoDB dependencies...")
dependencies = ["dirmngr", "gnupg", "apt-transport-https", "ca-certificates", "software-properties-common"]
for dep in dependencies:
    if not is_installed(dep):
        run_command(f"sudo apt-get install -y {dep}", f"Failed to install {dep}")

# Add MongoDB GPG key and list file if not already added
if not os.path.exists("/usr/share/keyrings/mongodb-server-7.0.gpg"):
    run_command("curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg",
                "Failed to import MongoDB GPG key")
if not os.path.exists("/etc/apt/sources.list.d/mongodb-org-7.0.list"):
    run_command("echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list",
                "Failed to create MongoDB list file")

run_command("sudo apt-get update", "Failed to update package lists")

# Step 2: Install libssl1.1 if not installed
if not is_installed("libssl1.1"):
    print("Installing libssl1.1...")
    run_command("wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb",
                "Failed to download libssl1.1")
    run_command("sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb", "Failed to install libssl1.1")
    run_command("sudo apt-get update", "Failed to update package lists after installing libssl1.1")

# Step 3: Install MongoDB if not installed
if not is_installed("mongodb-org"):
    print("Installing MongoDB...")
    run_command("sudo apt-get install -y mongodb-org", "Failed to install MongoDB")

# Step 4: Start MongoDB service if not running
print("Starting MongoDB service...")
run_command("sudo systemctl start mongod", "Failed to start MongoDB service")

# Step 5: Install MongoDB shell if not installed
if not is_installed("mongodb-mongosh"):
    print("Installing MongoDB shell...")
    run_command("sudo apt-get install -y mongodb-mongosh", "Failed to install MongoDB shell")

# Step 6: Create user in MongoDB if not already created
print("Creating MongoDB user...")
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

print("MongoDB setup complete and user 'manik' created successfully!")

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
    # Code to create new database if backup is not found

# Automated Backups
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

# Schedule Backup
take_backup()
