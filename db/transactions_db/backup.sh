#!/bin/bash

DB_NAME="$MYSQL_DATABASE"
DB_FILE=$DB_NAME"_db"
BACKUP_DIR="/var/lib/$DB_FILE/backup"

BACKUP_FILE="$BACKUP_DIR/$DB_FILE.sql"


MYSQL_USER="root"
PASSWORD=$MYSQL_ROOT_PASSWORD

echo "Backup started for database - $DB_NAME"

mysqldump --user=$MYSQL_USER --password=$PASSWORD $DB_NAME > $BACKUP_FILE

echo "Backup finished for database - $DB_NAME"



