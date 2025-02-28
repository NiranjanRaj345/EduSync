#!/bin/bash

# Exit on error
set -e

echo "Starting EduSync deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit 1
fi

# Configuration
APP_NAME="edusync"
APP_PATH="/var/www/$APP_NAME"
PYTHON_VERSION="3.12"
DOMAIN="yourdomain.com"

# Create application user if not exists
echo "Creating application user..."
id -u $APP_NAME &>/dev/null || useradd -m -s /bin/bash $APP_NAME

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python3-pip \
    nginx postgresql postgresql-contrib redis-server \
    build-essential libpq-dev supervisor certbot python3-certbot-nginx

# Create application directory
echo "Setting up application directory..."
mkdir -p $APP_PATH
chown -R $APP_NAME:www-data $APP_PATH

# Create logs directory
mkdir -p $APP_PATH/logs
chown -R $APP_NAME:www-data $APP_PATH/logs

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
su - $APP_NAME -c "cd $APP_PATH && python$PYTHON_VERSION -m venv venv"

# Install Python dependencies
echo "Installing Python dependencies..."
su - $APP_NAME -c "cd $APP_PATH && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Configure Nginx
echo "Configuring Nginx..."
cp nginx.conf /etc/nginx/sites-available/$APP_NAME
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Set up SSL certificates
echo "Setting up SSL certificates..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Configure systemd service
echo "Configuring systemd service..."
cp edusync.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME

# Set up database
echo "Setting up database..."
su - postgres -c "psql -c \"CREATE USER $APP_NAME WITH PASSWORD 'your_db_password';\""
su - postgres -c "psql -c \"CREATE DATABASE ${APP_NAME}_db OWNER $APP_NAME;\""

# Apply database migrations
echo "Applying database migrations..."
su - $APP_NAME -c "cd $APP_PATH && source venv/bin/activate && flask db upgrade"

# Set up Redis
echo "Configuring Redis..."
sed -i 's/# requirepass foobared/requirepass your_redis_password/' /etc/redis/redis.conf
systemctl restart redis-server

# Set correct permissions
echo "Setting permissions..."
chown -R $APP_NAME:www-data $APP_PATH
chmod -R 750 $APP_PATH
chmod -R 770 $APP_PATH/app/uploads
chmod -R 770 $APP_PATH/logs

# Set up logrotate
echo "Configuring log rotation..."
cat > /etc/logrotate.d/$APP_NAME << EOF
$APP_PATH/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 $APP_NAME www-data
    sharedscripts
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF

# Set up backup script
echo "Setting up backup script..."
cat > $APP_PATH/backup.sh << EOF
#!/bin/bash
BACKUP_DIR=$APP_PATH/backups
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup database
pg_dump ${APP_NAME}_db > \$BACKUP_DIR/db_\$DATE.sql

# Backup uploads
tar -czf \$BACKUP_DIR/uploads_\$DATE.tar.gz $APP_PATH/app/uploads

# Backup configuration
tar -czf \$BACKUP_DIR/config_\$DATE.tar.gz $APP_PATH/.env $APP_PATH/service-account.json

# Remove backups older than 7 days
find \$BACKUP_DIR -type f -mtime +7 -exec rm {} \;
EOF

chmod +x $APP_PATH/backup.sh
chown $APP_NAME:www-data $APP_PATH/backup.sh

# Add backup cron job
echo "Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 3 * * * $APP_PATH/backup.sh") | crontab -

echo "Deployment completed successfully!"
echo "Please update the following files with your configuration:"
echo "1. $APP_PATH/.env"
echo "2. $APP_PATH/service-account.json"
echo "3. Update passwords in database and Redis configuration"
echo "4. Update domain name in Nginx configuration"

# Final check
systemctl status $APP_NAME
nginx -t
echo "Visit https://$DOMAIN to access your application"
