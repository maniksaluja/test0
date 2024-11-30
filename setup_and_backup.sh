#!/bin/bash

# Function to install MongoDB if not already installed
install_mongodb() {
    if ! command -v mongo &> /dev/null; then
        echo "MongoDB is not installed. Installing MongoDB..."
        wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-org-5.0.gpg
        echo "deb [signed-by=/usr/share/keyrings/mongodb-org-5.0.gpg] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
        sudo apt update -y
        sudo apt install -y mongodb-org
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
    
    # Check if mongodump is available before proceeding
    if ! command -v mongodump &> /dev/null; then
        echo "mongodump command not found. Aborting backup."
        return 1
    fi

    # Perform the backup
    mongodump --db manik --out "$BACKUP_DIR/$BACKUP_NAME"
    
    # Check if backup was successful
    if [[ ! -d "$BACKUP_DIR/$BACKUP_NAME" ]]; then
        echo "Backup failed. Directory $BACKUP_DIR/$BACKUP_NAME not created."
        return 1
    fi

    # Compress the backup
    tar -czvf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
    
    # Check if the tar file was created
    if [[ ! -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]]; then
        echo "Backup tar file creation failed."
        return 1
    fi

    # Send backup to Telegram
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    MESSAGE="New MongoDB backup: $BACKUP_NAME"

    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id="$CHAT_ID" \
        -d text="$MESSAGE"

    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendDocument" \
        -F chat_id="$CHAT_ID" \
        -F document=@"$BACKUP_FILE"

    echo "Backup performed and sent to Telegram."
    
    # Cleanup: Remove old backups older than 7 days
    find "$BACKUP_DIR" -type f -mtime +7 -name '*.tar.gz' -exec rm {} \;
}

# Function to check and manage collection size
check_collection_size() {
    DB_NAME="manik"
    COLLECTION_NAME="auto_delete"
    LIMIT_MB=50
    DELETE_AMOUNT_MB=40
    LIMIT_BYTES=$((LIMIT_MB * 1024 * 1024))
    DELETE_AMOUNT_BYTES=$((DELETE_AMOUNT_MB * 1024 * 1024))
    
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
    # Run backup only if the previous backup was successful
    if perform_backup; then
        check_collection_size
    else
        echo "Backup failed, skipping collection size check."
    fi
fi
