#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.sql.gz>"
    echo "Available backups:"
    ls -lh ./backups/backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "========================================="
echo "Database Restore Script"
echo "========================================="

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "Error: .env.production file not found!"
    exit 1
fi

echo "WARNING: This will overwrite the current database!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Decompressing backup..."
gunzip -c $BACKUP_FILE > /tmp/restore.sql

echo "Restoring database..."
docker compose -f docker-compose.prod.yml exec -T db psql -U ${DB_USER} ${DB_NAME} < /tmp/restore.sql

echo "Cleaning up..."
rm /tmp/restore.sql

echo "Database restored successfully!"
echo "========================================="

