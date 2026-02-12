# Docker Deployment Guide

## Quick Start

### 1. Build and Start All Services

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache/message broker (port 6379)
- Django web application (port 8000)
- Celery worker (for async tasks)
- Celery beat (for scheduled tasks)

### 2. Access the Application

Open your browser and navigate to: **http://localhost:8000**

**Default Login Credentials:**
- Username: `admin`
- Password: `admin123`

## Docker Commands

### Start services in detached mode
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (clean slate)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### Rebuild containers
```bash
docker-compose up --build
```

### Run Django management commands
```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic

# Access Django shell
docker-compose exec web python manage.py shell
```

### Access container shell
```bash
docker-compose exec web bash
docker-compose exec db psql -U postgres -d smart_task_db
docker-compose exec redis redis-cli
```

## Services Overview

### Web (Django Application)
- **Container:** smart_task_web
- **Port:** 8000
- **Command:** Gunicorn WSGI server with 3 workers
- **Depends on:** PostgreSQL, Redis

### Database (PostgreSQL)
- **Container:** smart_task_db
- **Port:** 5432
- **Image:** postgres:15-alpine
- **Credentials:** postgres/password
- **Database:** smart_task_db

### Cache/Broker (Redis)
- **Container:** smart_task_redis
- **Port:** 6379
- **Image:** redis:7-alpine

### Celery Worker
- **Container:** smart_task_celery_worker
- **Purpose:** Process async tasks (email notifications)

### Celery Beat
- **Container:** smart_task_celery_beat
- **Purpose:** Schedule periodic tasks (daily summaries, hourly reminders)

## Environment Variables

Environment variables are configured in `docker-compose.yml`. For production, create a `.env` file:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=strong-password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Production Deployment

For production:

1. Update `SECRET_KEY` to a strong random value
2. Set `DEBUG=False`
3. Configure proper `ALLOWED_HOSTS`
4. Use strong database password
5. Configure real email backend (SMTP)
6. Use environment-specific docker-compose file
7. Set up SSL/TLS certificates
8. Use a reverse proxy (nginx)

## Troubleshooting

### Database connection errors
```bash
# Check if database is healthy
docker-compose ps

# View database logs
docker-compose logs db
```

### Redis connection errors
```bash
# Check Redis status
docker-compose exec redis redis-cli ping
```

### Static files not loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Reset everything
```bash
docker-compose down -v
docker-compose up --build
```

## Data Persistence

Docker volumes are used for data persistence:
- `postgres_data`: Database files
- `static_volume`: Static files (CSS, JS, images)
- `media_volume`: User-uploaded media files

These volumes persist even when containers are stopped or removed.

