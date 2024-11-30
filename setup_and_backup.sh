#!/bin/bash

# Function to install MongoDB if not already installed
install_mongodb() {
    if ! command -v mongo &> /dev/null; then
        echo "MongoDB is not installed. Installing MongoDB..."
        
        # Add MongoDB repository for Ubuntu Jammy (22.04)
        wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-org-5.0.gpg
        echo "deb [signed-by=/usr/share/keyrings/mongodb-org-5.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
        
        # Update package list and install MongoDB and MongoDB tools
        sudo apt update -y
        sudo apt install -y mongodb-org mongodb-org-tools
        
        # Start and enable MongoDB service
        sudo systemctl start mongod
        sudo systemctl enable mongod
    else
        echo "MongoDB is already installed."
    fi
}

# Function to install jq if not already installed
install_jq() {
    if ! command -v jq &> /dev/null; then
        echo "jq is not installed. Installing jq..."
        sudo apt update -y
        sudo apt install -y jq
    else
        echo "jq is already installed."
    fi
}

# Function to check for existing backups in Telegram
check_existing_backup() {
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    EXISTING_BACKUP=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates" | jq -r '.result[].message.document.file_name // empty' | head -n 1)
    
    if [[ ! -z "$EXISTING_BACKUP" ]]; then
        echo "Existing backup found: $EXISTING_BACKUP"
        return 0
    else
        echo "No existing backup found."
        return 1
    fi
}

# Function to perform MongoDB backup and send to Telegram
perform_backup() {
    BACKUP_DIR="/home/ubuntu/backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +"%F_%T")
    BACKUP_NAME="mongodb_backup_$TIMESTAMP"
    mongodump --db manik --out "$BACKUP_DIR/$BACKUP_NAME"

    tar -czvf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    MESSAGE="New MongoDB backup: $BACKUP_NAME"

    # Send message with backup info
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id="$CHAT_ID" \
        -d text="$MESSAGE"

    # Send the backup file
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendDocument" \
        -F chat_id="$CHAT_ID" \
        -F document=@"$BACKUP_FILE"

    # Delete backups older than 7 days
    find "$BACKUP_DIR" -type f -mtime +7 -name '*.tar.gz' -exec rm {} \;
    echo "Backup performed and sent to Telegram."
}

# Function to check and manage collection size
check_collection_size() {
    DB_NAME="manik"
    COLLECTION_NAME="auto_delete"
    LIMIT_MB=50
    DELETE_AMOUNT_MB=40
    LIMIT_BYTES=$((LIMIT_MB * 1024 * 1024))
    DELETE_AMOUNT_BYTES=$((DELETE_AMOUNT_MB * 1024 * 1024))
    
    # Get current collection size
    current_size=$(mongo --quiet --eval "db.$COLLECTION_NAME.stats().size" "$DB_NAME")

    if (( current_size > LIMIT_BYTES )); then
        echo "Collection size exceeded limit. Current size: $((current_size / 1024 / 1024)) MB"
        delete_query="db.$COLLECTION_NAME.find({}, {_id: 1}).sort({timestamp: 1}).limit($((DELETE_AMOUNT_BYTES / 1024 / 1024)))"
        mongo --quiet --eval "$delete_query.forEach(doc => db.$COLLECTION_NAME.deleteOne({_id: doc._id}));" "$DB_NAME"
        echo "Deleted $DELETE_AMOUNT_MB MB of old data."
    else
        echo "Collection size within limit. Current size: $((current_size / 1024 / 1024)) MB"
    fi
}

# Main script execution
install_mongodb
install_jq

if check_existing_backup; then
    echo "Using existing backup."
else
    perform_backup
    check_collection_size
fi
