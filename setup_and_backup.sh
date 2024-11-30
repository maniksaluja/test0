#!/bin/bash

# Function to install MySQL if not already installed
install_mysql() {
    if ! command -v mysql &> /dev/null
    then
        echo "MySQL is not installed. Installing MySQL..."
        
        sudo apt update -y
        sudo apt install -y mysql-server
        sudo systemctl start mysql
        sudo systemctl enable mysql
    else
        echo "MySQL is already installed."
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

# Function to perform MySQL backup and send to Telegram
perform_backup() {
    BACKUP_DIR="/home/ubuntu/backups"
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +"%F_%T")
    BACKUP_NAME="mysql_backup_$TIMESTAMP"
    
    # MySQL Database Details
    DB_NAME="manik"
    DB_USER="your_db_user"
    DB_PASS="your_db_password"
    
    # Backup MySQL database
    mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/$BACKUP_NAME.sql

    # Compress the Backup
    tar -czvf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $BACKUP_DIR $BACKUP_NAME.sql

    # Telegram Bot Details
    BOT_TOKEN="7773860912:AAHo6aHZcV61VvaF_ymqY6_n7bneICOBbfo"
    CHAT_ID="-1002263879722"
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    MESSAGE="New MySQL backup: $BACKUP_NAME"

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

# Main script execution
install_mysql

if check_existing_backup; then
    echo "Using existing backup."
else
    perform_backup
fi
