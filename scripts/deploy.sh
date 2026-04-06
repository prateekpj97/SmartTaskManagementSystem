#!/bin/bash

set -e

echo "========================================="
echo "Smart Task Management System - Production Deployment"
echo "========================================="

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "Error: .env.production file not found!"
    echo "Please copy .env.production.example and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

echo "Step 1: Pulling latest changes from repository..."
git pull origin main

echo "Step 2: Building Docker images..."
docker compose -f docker-compose.prod.yml build --no-cache

echo "Step 3: Stopping existing containers..."
docker compose -f docker-compose.prod.yml down

echo "Step 4: Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "Step 5: Waiting for database to be ready..."
sleep 10

echo "Step 6: Running database migrations..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

echo "Step 7: Collecting static files..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo "Step 8: Creating superuser (if needed)..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')
    print('Superuser created. Please change the password!')
else:
    print('Superuser already exists.')
EOF

echo "Step 9: Checking service health..."
sleep 5
docker compose -f docker-compose.prod.yml ps

echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Services running:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "View logs with: docker compose -f docker-compose.prod.yml logs -f"
echo "Stop services with: docker compose -f docker-compose.prod.yml down"

