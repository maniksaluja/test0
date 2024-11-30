#!/bin/bash

# Function to install MongoDB if not already installed
install_mongodb() {
    if ! command -v mongo &> /dev/null
    then
        echo "MongoDB is not installed. Installing MongoDB..."
        
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        
        sudo apt update -y
        sudo apt install -y mongodb-org
        sudo systemctl start mongod
        sudo systemctl enable mongod
    else
        echo "MongoDB is already installed."
    fi
}

# Function to check for existing backups in Telegram
check_existing_backup() {
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    EXISTING_BACKUP=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates" | grep -oP '(?<=document.file_name":")[^"]*')
    
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
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +"%F_%T")
    BACKUP_NAME="mongodb_backup_$TIMESTAMP"
    mongodump --db manik --out $BACKUP_DIR/$BACKUP_NAME

    # Compress the Backup
    tar -czvf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $BACKUP_DIR $BACKUP_NAME

    # Telegram Bot Details
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    MESSAGE="New MongoDB backup: $BACKUP_NAME"

    # Send Message and File to Telegram
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="$MESSAGE"

    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendDocument" \
        -F chat_id=$CHAT_ID \
        -F document=@"$BACKUP_FILE"

    # Clean up old backups
    find $BACKUP_DIR -type f -mtime +7 -name '*.tar.gz' -exec rm {} \;

    echo "Backup performed and sent to Telegram."
}

# Function to check and manage collection size
check_collection_size() {
    DB_NAME="manik"
    COLLECTION_NAME="auto_delete"
    LIMIT_MB=50
    DELETE_AMOUNT_MB=40

    # Convert MB to bytes
    LIMIT_BYTES=$((LIMIT_MB * 1024 * 1024))
    DELETE_AMOUNT_BYTES=$((DELETE_AMOUNT_MB * 1024 * 1024))

    # Get current collection size
    current_size=$(mongo --eval "db.$COLLECTION_NAME.dataSize()" $DB_NAME --quiet)

    if (( current_size > LIMIT_BYTES )); then
        echo "Collection size exceeded limit. Current size: $(($current_size / 1024 / 1024)) MB"
        
        # Delete oldest data
        delete_query="db.$COLLECTION_NAME.find().sort({timestamp: 1}).limit($((DELETE_AMOUNT_BYTES / 1024 / 1024)))"
        mongo --eval "$delete_query.forEach(function(doc) { db.$COLLECTION_NAME.remove({_id: doc._id}); })" $DB_NAME --quiet

        echo "Deleted $DELETE_AMOUNT_MB MB of old data."
    else
        echo "Collection size within limit. Current size: $(($current_size / 1024 / 1024)) MB"
    fi
}

# Main script execution
install_mongodb

if check_existing_backup; then
    echo "Using existing backup."
else
    perform_backup
    check_collection_size
fi
