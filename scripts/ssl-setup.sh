#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: ./ssl-setup.sh <your-domain.com>"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo "========================================="
echo "SSL Certificate Setup with Let's Encrypt"
echo "========================================="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Create required directories
mkdir -p certbot/conf
mkdir -p certbot/www

echo "Step 1: Requesting SSL certificate..."
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo ""
echo "Step 2: Updating nginx configuration..."
sed -i "s/yourdomain.com/$DOMAIN/g" nginx/conf.d/smart_task.conf

echo ""
echo "Step 3: Reloading nginx..."
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo ""
echo "========================================="
echo "SSL certificate installed successfully!"
echo "========================================="
echo ""
echo "Your site is now accessible at: https://$DOMAIN"
echo ""
echo "Certificate will auto-renew via certbot container."

