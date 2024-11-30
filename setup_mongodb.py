import os

def run_command(command, error_message):
    result = os.system(command)
    if result != 0:
        print(f"Error: {error_message}")
        exit(1)

# Step 1: Install MongoDB dependencies
print("Installing MongoDB dependencies...")
run_command("curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg",
            "Failed to import MongoDB GPG key")
run_command("echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list",
            "Failed to create MongoDB list file")
run_command("sudo apt-get update", "Failed to update package lists")

# Step 2: Install libssl1.1
print("Installing libssl1.1...")
run_command("sudo apt-get install -y dirmngr gnupg apt-transport-https ca-certificates software-properties-common",
            "Failed to install dependencies")
run_command("wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb",
            "Failed to download libssl1.1")
run_command("sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb", "Failed to install libssl1.1")
run_command("sudo apt-get update", "Failed to update package lists after installing libssl1.1")

# Step 3: Install MongoDB
print("Installing MongoDB...")
run_command("sudo apt-get install -y mongodb-org", "Failed to install MongoDB")

# Step 4: Start MongoDB service
print("Starting MongoDB service...")
run_command("sudo systemctl start mongod", "Failed to start MongoDB service")
run_command("sudo systemctl status mongod", "MongoDB service is not running")

# Step 5: Install MongoDB shell
print("Installing MongoDB shell...")
run_command("sudo apt-get install -y mongodb-mongosh", "Failed to install MongoDB shell")

# Step 6: Create user in MongoDB
print("Creating MongoDB user...")
mongo_commands = """
mongosh <<EOF
use myNewDatabase
db.createUser({
  user: "manik",
  pwd: "manik",
  roles: [{ role: "readWrite", db: "myNewDatabase" }]
})
EOF
"""
run_command(mongo_commands, "Failed to create MongoDB user")

print("MongoDB setup complete and user 'manik' created successfully!")
