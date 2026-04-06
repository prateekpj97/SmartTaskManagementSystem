# 🚀 Production Deployment Guide

## Smart Task Management System - Production Setup

This guide covers deploying the Smart Task Management System to a production environment using Docker, Nginx, PostgreSQL, Redis, and SSL certificates.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Environment Configuration](#environment-configuration)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Deployment](#deployment)
6. [Post-Deployment](#post-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Backup & Restore](#backup--restore)
9. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Server Requirements

- **OS**: Ubuntu 20.04 LTS or later (recommended)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 20GB SSD
- **CPU**: 2+ cores recommended
- **Domain**: A registered domain name pointing to your server

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- A domain name with DNS configured

---

## 🖥️ Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### 3. Install Git

```bash
sudo apt install git -y
```

### 4. Configure Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## ⚙️ Environment Configuration

### 1. Clone Repository

```bash
cd /opt
sudo git clone <your-repository-url> smart-task-app
cd smart-task-app
sudo chown -R $USER:$USER .
```

### 2. Configure Environment Variables

```bash
# Copy production environment template
cp .env.production .env.production.local

# Edit with your actual values
nano .env.production.local
```

### Required Environment Variables

```bash
# Django Settings
DEBUG=False
SECRET_KEY=<generate-strong-secret-key-min-50-chars>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database
DB_NAME=smart_task_production_db
DB_USER=smart_task_user
DB_PASSWORD=<strong-database-password>
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<strong-redis-password>

# Celery
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/0

# Email (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. Generate Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## ✅ Post-Deployment

### 1. Verify Services

```bash
# Check all containers are running
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f celery_worker
docker compose -f docker-compose.prod.yml logs -f nginx
```

### 2. Test Application

```bash
# Health check
curl https://yourdomain.com/health/

# Expected response:
# {"status": "healthy", "database": "connected", "cache": "connected"}
```

### 3. Access Admin Panel

- URL: `https://yourdomain.com/admin/`
- Login with superuser credentials created during deployment

### 4. Configure Periodic Tasks

1. Login to admin panel
2. Navigate to **Periodic Tasks** (Django Celery Beat)
3. Verify scheduled tasks are configured:
   - Daily task summary (8:00 AM)
   - Hourly deadline reminders

---

## 📊 Monitoring & Maintenance

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

### Monitor Resources

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Application Logs

Logs are stored in `./logs/` directory:
- `django.log` - Django application logs
- `celery.log` - Celery worker logs

```bash
# View Django logs
tail -f logs/django.log

# View Celery logs
tail -f logs/celery.log
```

---

## 💾 Backup & Restore

### Automated Backup

```bash
# Run backup script
./scripts/backup.sh

# Backups are stored in ./backups/ directory
# Format: backup_YYYYMMDD_HHMMSS.sql.gz
```

### Setup Automated Daily Backups

```bash
# Add to crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /opt/smart-task-app && ./scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Restore from Backup

```bash
# List available backups
ls -lh backups/

# Restore specific backup
./scripts/restore.sh backups/backup_20260212_020000.sql.gz
```

### Manual Backup

```bash
# Database backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U smart_task_user smart_task_production_db > backup.sql

# Media files backup
tar -czf media_backup.tar.gz media/
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Restart Services

```bash
# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart celery_worker
```

### Scale Services

```bash
# Scale celery workers
docker compose -f docker-compose.prod.yml up -d --scale celery_worker=4
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs <service-name>

# Check container status
docker compose -f docker-compose.prod.yml ps
```

#### 2. Database Connection Error

```bash
# Check database is running
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Verify credentials in .env.production.local
```

#### 3. Static Files Not Loading

```bash
# Collect static files again
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check nginx logs
docker compose -f docker-compose.prod.yml logs nginx
```

#### 4. SSL Certificate Issues

```bash
# Check certificate files
ls -la certbot/conf/live/yourdomain.com/

# Renew certificate manually
docker compose -f docker-compose.prod.yml run --rm certbot renew

# Reload nginx
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

#### 5. Email Not Sending

```bash
# Check celery worker logs
docker compose -f docker-compose.prod.yml logs celery_worker

# Test email configuration
docker compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase worker processes (in docker-compose.prod.yml)
# Modify gunicorn workers: --workers 8

# Scale celery workers
docker compose -f docker-compose.prod.yml up -d --scale celery_worker=4
```

---

## 🔐 Security Best Practices

### 1. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 2. Firewall Configuration

```bash
# Only allow necessary ports
sudo ufw status
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Change Default Passwords

- Change admin password after first login
- Use strong database passwords
- Rotate SECRET_KEY periodically

### 4. Monitor Logs

```bash
# Check for suspicious activity
tail -f logs/django.log | grep -i "error\|warning\|failed"
```

### 5. Enable Fail2Ban (Optional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📞 Support & Resources

### Useful Commands Reference

```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Execute command in container
docker compose -f docker-compose.prod.yml exec web <command>

# Access Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Health Monitoring

- **Health Check Endpoint**: `https://yourdomain.com/health/`
- **Admin Panel**: `https://yourdomain.com/admin/`
- **API Documentation**: `https://yourdomain.com/api/`

---

## 📝 Checklist

Before going live, ensure:

- [ ] Domain DNS configured correctly
- [ ] SSL certificate installed and working
- [ ] Environment variables configured
- [ ] Database backups automated
- [ ] Firewall configured
- [ ] Admin password changed from default
- [ ] Email configuration tested
- [ ] Health check endpoint responding
- [ ] Monitoring/logging configured
- [ ] Static files serving correctly
- [ ] Celery workers running
- [ ] Periodic tasks configured

---

## 🎉 Congratulations!

Your Smart Task Management System is now running in production!

**Next Steps:**
1. Monitor application logs regularly
2. Set up automated backups
3. Configure monitoring alerts
4. Review security settings
5. Test all features in production

For issues or questions, check the troubleshooting section or review application logs.

---

**Last Updated**: 2026-02-12
**Version**: 1.0.0
## 🔒 SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended - Free)

```bash
# Update domain in nginx config
nano nginx/conf.d/smart_task.conf
# Replace 'yourdomain.com' with your actual domain

# Run SSL setup script
./scripts/ssl-setup.sh yourdomain.com admin@yourdomain.com
```

### Option 2: Manual Certificate

If you have your own SSL certificates:

```bash
# Copy certificates
mkdir -p certbot/conf/live/yourdomain.com/
cp fullchain.pem certbot/conf/live/yourdomain.com/
cp privkey.pem certbot/conf/live/yourdomain.com/
```

---

## 🚀 Deployment

### Automated Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### Manual Deployment Steps

```bash
# 1. Build images
docker compose -f docker-compose.prod.yml build

# 2. Start services
docker compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 5. Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---


