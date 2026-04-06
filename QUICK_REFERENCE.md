# ⚡ Quick Reference Guide

## Smart Task Management System - Common Commands

---

## 🚀 Deployment

```bash
# Initial deployment
./scripts/deploy.sh

# Update deployment
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🐳 Docker Commands

### Start/Stop Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stop all services
docker compose -f docker-compose.prod.yml down

# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart web
```

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f celery_worker
docker compose -f docker-compose.prod.yml logs -f nginx

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 web
```

### Container Management

```bash
# List running containers
docker compose -f docker-compose.prod.yml ps

# Execute command in container
docker compose -f docker-compose.prod.yml exec web <command>

# Access container shell
docker compose -f docker-compose.prod.yml exec web bash

# View container stats
docker stats
```

---

## 🗄️ Database Operations

### Migrations

```bash
# Create migrations
docker compose -f docker-compose.prod.yml exec web python manage.py makemigrations

# Apply migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Show migrations
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations
```

### Database Shell

```bash
# Django dbshell
docker compose -f docker-compose.prod.yml exec web python manage.py dbshell

# PostgreSQL shell
docker compose -f docker-compose.prod.yml exec db psql -U smart_task_user smart_task_production_db
```

### Backup & Restore

```bash
# Create backup
./scripts/backup.sh

# Restore backup
./scripts/restore.sh backups/backup_YYYYMMDD_HHMMSS.sql.gz

# Manual backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U smart_task_user smart_task_production_db > backup.sql
```

---

## 👤 User Management

```bash
# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Change user password
docker compose -f docker-compose.prod.yml exec web python manage.py changepassword <username>

# Django shell for user operations
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

---

## 📁 Static Files

```bash
# Collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Clear static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --clear --noinput
```

---

## 🔄 Celery Operations

```bash
# View celery worker logs
docker compose -f docker-compose.prod.yml logs -f celery_worker

# View celery beat logs
docker compose -f docker-compose.prod.yml logs -f celery_beat

# Restart celery workers
docker compose -f docker-compose.prod.yml restart celery_worker celery_beat

# Scale celery workers
docker compose -f docker-compose.prod.yml up -d --scale celery_worker=4
```

---

## 🌐 Nginx Operations

```bash
# View nginx logs
docker compose -f docker-compose.prod.yml logs -f nginx

# Test nginx configuration
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Restart nginx
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 🔒 SSL Certificate

```bash
# Setup SSL (first time)
./scripts/ssl-setup.sh yourdomain.com

# Renew certificate manually
docker compose -f docker-compose.prod.yml run --rm certbot renew

# Check certificate expiry
docker compose -f docker-compose.prod.yml run --rm certbot certificates
```

---

## 🔍 Debugging

```bash
# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Check deployment settings
docker compose -f docker-compose.prod.yml exec web python manage.py check --deploy

# View environment variables
docker compose -f docker-compose.prod.yml exec web env

# Test database connection
docker compose -f docker-compose.prod.yml exec web python manage.py dbshell

# Test email
docker compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

---

## 📊 Monitoring

```bash
# Health check
curl https://yourdomain.com/health/

# Container resource usage
docker stats

# Disk usage
docker system df

# View application logs
tail -f logs/django.log
tail -f logs/celery.log
```

---

## 🧹 Cleanup

```bash
# Remove stopped containers
docker compose -f docker-compose.prod.yml rm

# Clean up unused Docker resources
docker system prune -a

# Clean up volumes (WARNING: deletes data)
docker volume prune
```

---

## 🔄 Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Update specific service
docker compose -f docker-compose.prod.yml up -d --build web
```

---

## 🚨 Emergency Commands

```bash
# Stop everything immediately
docker compose -f docker-compose.prod.yml down

# View recent errors
docker compose -f docker-compose.prod.yml logs --tail=100 | grep -i error

# Restart all services
docker compose -f docker-compose.prod.yml restart

# Force recreate containers
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

---

## 📞 Useful URLs

- **Application**: `https://yourdomain.com`
- **Admin Panel**: `https://yourdomain.com/admin/`
- **API**: `https://yourdomain.com/api/`
- **Health Check**: `https://yourdomain.com/health/`

---

## 💡 Tips

1. Always backup before major changes
2. Test in development first
3. Monitor logs after deployments
4. Keep environment variables secure
5. Regular security updates
6. Document custom changes

---

**For detailed information, see:**
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Full deployment guide
- [SECURITY.md](SECURITY.md) - Security best practices
- [README.md](README.md) - Project overview

