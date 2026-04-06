#!/bin/bash

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${TIMESTAMP}.sql"

echo "========================================="
echo "Database Backup Script"
echo "========================================="

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "Error: .env.production file not found!"
    exit 1
fi

echo "Creating database backup..."
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U ${DB_USER} ${DB_NAME} > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress the backup
echo "Compressing backup..."
gzip ${BACKUP_DIR}/${BACKUP_FILE}

echo "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.gz"

# Remove backups older than 30 days
echo "Cleaning up old backups (older than 30 days)..."
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed successfully!"
echo "========================================="

