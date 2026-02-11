#!/bin/bash

# Smart Task Management System Setup Script

echo "=========================================="
echo "Smart Task Management System Setup"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL database exists
echo "Checking PostgreSQL database..."
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='smart_task_db'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating PostgreSQL database..."
    sudo -u postgres psql -c "CREATE DATABASE smart_task_db;"
    echo "Database created successfully!"
else
    echo "Database already exists."
fi

# Run migrations
echo "Running migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser (optional)
echo ""
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 manage.py createsuperuser
fi

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "1. Start Redis: redis-server"
echo "2. Start Celery Worker: celery -A smart_task_management worker --loglevel=info"
echo "3. Start Celery Beat: celery -A smart_task_management beat --loglevel=info"
echo "4. Start Django: python3 manage.py runserver"
echo ""
echo "Visit http://localhost:8000 in your browser"
echo ""

