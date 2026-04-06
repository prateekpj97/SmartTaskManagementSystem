# 🔐 Security Configuration Guide

## Smart Task Management System - Security Best Practices

---

## 🛡️ Security Checklist

### Pre-Production Security

- [ ] **SECRET_KEY**: Generate strong, unique secret key (50+ characters)
- [ ] **DEBUG**: Set to `False` in production
- [ ] **ALLOWED_HOSTS**: Configure with actual domain names only
- [ ] **Database Password**: Use strong, unique password (16+ characters)
- [ ] **Redis Password**: Enable and use strong password
- [ ] **SSL/TLS**: Install valid SSL certificate
- [ ] **HTTPS**: Force HTTPS redirect enabled
- [ ] **Security Headers**: All security headers configured
- [ ] **Admin URL**: Consider changing from `/admin/` to custom path
- [ ] **Default Passwords**: Change all default passwords

---

## 🔑 Environment Variables Security

### Never Commit Sensitive Data

Add to `.gitignore`:
```
.env
.env.production
.env.production.local
*.pem
*.key
certbot/
```

### Secure Storage

- Store `.env.production` outside repository
- Use environment variable management tools (AWS Secrets Manager, HashiCorp Vault)
- Restrict file permissions:
  ```bash
  chmod 600 .env.production
  ```

---

## 🌐 Network Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH (consider changing port)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Recommended settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Change from default 22
```

---

## 🔒 Django Security Settings

### Enabled in Production

```python
# In settings.py (already configured)
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Additional Recommendations

```python
# Add to settings.py for extra security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
```

---

## 🗄️ Database Security

### PostgreSQL Hardening

```bash
# Access PostgreSQL container
docker compose -f docker-compose.prod.yml exec db psql -U smart_task_user

# Change password
ALTER USER smart_task_user WITH PASSWORD 'new_strong_password';

# Restrict connections (in postgresql.conf)
listen_addresses = 'localhost'
```

### Backup Encryption

```bash
# Encrypt backups
gpg --symmetric --cipher-algo AES256 backup.sql

# Decrypt when needed
gpg --decrypt backup.sql.gpg > backup.sql
```

---

## 🔴 Redis Security

### Enable Authentication

Already configured in `docker-compose.prod.yml`:
```yaml
redis:
  command: redis-server --requirepass ${REDIS_PASSWORD}
```

### Additional Redis Security

```bash
# Disable dangerous commands
redis-cli CONFIG SET rename-command FLUSHDB ""
redis-cli CONFIG SET rename-command FLUSHALL ""
redis-cli CONFIG SET rename-command CONFIG ""
```

---

## 📧 Email Security

### Use App-Specific Passwords

For Gmail:
1. Enable 2-Factor Authentication
2. Generate App-Specific Password
3. Use in `EMAIL_HOST_PASSWORD`

### Email Encryption

```python
# Already configured
EMAIL_USE_TLS = True
EMAIL_PORT = 587
```

---

## 🚨 Monitoring & Alerts

### Log Monitoring

```bash
# Monitor for failed login attempts
tail -f logs/django.log | grep "Failed login"

# Monitor for errors
tail -f logs/django.log | grep "ERROR"
```

### Setup Fail2Ban

```bash
# Install
sudo apt install fail2ban -y

# Configure for nginx
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-noscript]
enabled = true
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 3600
```

---

## 🔍 Security Auditing

### Regular Security Checks

```bash
# Check for security updates
sudo apt update
sudo apt list --upgradable

# Scan for vulnerabilities
docker scan smart_task_web_prod

# Check Python dependencies
pip list --outdated
```

### Django Security Check

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py check --deploy
```

---

## 🛠️ Incident Response

### If Compromised

1. **Immediate Actions**:
   ```bash
   # Stop all services
   docker compose -f docker-compose.prod.yml down
   
   # Change all passwords
   # Rotate SECRET_KEY
   # Review logs for suspicious activity
   ```

2. **Investigation**:
   ```bash
   # Check access logs
   tail -n 1000 logs/django.log
   docker compose -f docker-compose.prod.yml logs nginx
   
   # Check for unauthorized users
   docker compose -f docker-compose.prod.yml exec web python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.all()
   ```

3. **Recovery**:
   - Restore from clean backup
   - Update all dependencies
   - Implement additional security measures
   - Monitor closely for 48 hours

---

## 📋 Security Maintenance Schedule

### Daily
- Monitor application logs
- Check error rates

### Weekly
- Review access logs
- Check for failed login attempts
- Verify backups are working

### Monthly
- Update system packages
- Update Docker images
- Review user accounts
- Rotate credentials
- Security audit

### Quarterly
- Full security assessment
- Penetration testing
- Update SSL certificates (if not auto-renewing)
- Review and update security policies

---

## 🔗 Security Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

**Remember**: Security is an ongoing process, not a one-time setup!

