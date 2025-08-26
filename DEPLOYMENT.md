# ML Gruppe Helpdesk - Deployment Guide

## Overview

This document provides comprehensive deployment instructions for the ML Gruppe Helpdesk system, supporting both Docker containerized deployment and traditional server installation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Traditional Server Deployment](#traditional-server-deployment)
5. [Database Setup](#database-setup)
6. [SSL Configuration](#ssl-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: Minimum 2 cores, recommended 4+ cores
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB free space
- **OS**: Ubuntu 20.04+, CentOS 8+, or Docker-compatible system

### Software Requirements

- Docker 20.10+
- Docker Compose 1.29+
- Git
- OpenSSL (for SSL certificates)

## Environment Configuration

### 1. Clone Repository

```bash
git clone https://github.com/mlgruppe/helpdesk.git
cd helpdesk
```

### 2. Environment Variables

Copy the appropriate environment template:

```bash
# For development
cp .env.example .env

# For production
cp .env.production .env
```

### 3. Required Configuration

Edit `.env` file with your specific values:

```bash
# Essential configurations
SECRET_KEY=your-super-secret-key-here
MICROSOFT_CLIENT_ID=your-azure-app-client-id
MICROSOFT_CLIENT_SECRET=your-azure-app-secret
MICROSOFT_TENANT_ID=your-azure-tenant-id
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=your-email-password

# Database passwords
MYSQL_ROOT_PASSWORD=secure-root-password
MYSQL_PASSWORD=secure-user-password

# Optional but recommended
CLAUDE_API_KEY=your-claude-api-key
TEAMS_WEBHOOK_URL=your-teams-webhook-url
SENTRY_DSN=your-sentry-dsn
```

## Docker Deployment

### Quick Start

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to development environment
./deploy.sh dev deploy

# Deploy to production environment
./deploy.sh production deploy
```

### Manual Docker Deployment

#### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
docker-compose -f docker-compose.dev.yml exec web flask db init
docker-compose -f docker-compose.dev.yml exec web flask db migrate
docker-compose -f docker-compose.dev.yml exec web flask db upgrade
docker-compose -f docker-compose.dev.yml exec web flask deploy
```

#### Production Environment

```bash
# Build and start production environment
docker-compose up -d --build

# Initialize database
docker-compose exec web flask db upgrade
docker-compose exec web flask deploy

# Check status
docker-compose ps
```

### Service Architecture

The Docker deployment includes:

- **web**: Main Flask application (Gunicorn + 4 workers)
- **mysql**: MySQL 8.0 database
- **redis**: Redis for caching and queues
- **celery**: Background task worker
- **celery-beat**: Scheduled task scheduler
- **nginx**: Reverse proxy (production profile)
- **mongodb**: Optional MongoDB (advanced features)

## Traditional Server Deployment

### 1. System Preparation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server redis-server nginx

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip mysql-server redis nginx
```

### 2. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash helpdesk
sudo su - helpdesk

# Clone and setup application
git clone https://github.com/mlgruppe/helpdesk.git
cd helpdesk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# MySQL setup
sudo mysql_secure_installation

mysql -u root -p
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Initialize application database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask deploy
```

### 4. Process Management (Systemd)

Create service files:

```bash
# /etc/systemd/system/helpdesk.service
sudo nano /etc/systemd/system/helpdesk.service
```

```ini
[Unit]
Description=ML Gruppe Helpdesk
After=network.target mysql.service redis.service

[Service]
User=helpdesk
Group=helpdesk
WorkingDirectory=/home/helpdesk/helpdesk
Environment=PATH=/home/helpdesk/helpdesk/venv/bin
ExecStart=/home/helpdesk/helpdesk/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
sudo systemctl status helpdesk
```

## Database Setup

### MySQL Configuration

#### Development (SQLite)
SQLite database is automatically created at `helpdesk.db`.

#### Production (MySQL)

1. Install MySQL:
```bash
# Ubuntu/Debian
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
```

2. Configure MySQL:
```bash
sudo mysql_secure_installation
```

3. Create database:
```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk'@'%';
FLUSH PRIVILEGES;
```

### MongoDB Setup (Optional)

For advanced features:

```bash
# Install MongoDB
sudo apt install mongodb

# Configure replica set (for transactions)
echo "replication:" >> /etc/mongod.conf
echo "  replSetName: rs0" >> /etc/mongod.conf

# Initialize replica set
mongo --eval "rs.initiate()"
```

## SSL Configuration

### Let's Encrypt (Recommended for Production)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d helpdesk.mlgruppe.de

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Self-Signed Certificates (Development)

```bash
# Generate certificates
./deploy.sh production ssl

# Or manually:
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem
```

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:5000/health

# Service status
./deploy.sh production monitor

# View logs
./deploy.sh production logs
```

### Database Maintenance

```bash
# Create backup
./deploy.sh production backup

# Manual MySQL backup
mysqldump -u helpdesk -p helpdesk_db > backup_$(date +%Y%m%d).sql
```

### Log Management

Logs are stored in:
- Application: `logs/helpdesk.log`
- Nginx: `/var/log/nginx/`
- MySQL: `/var/log/mysql/`

### Performance Monitoring

1. **Sentry Integration**: Configure `SENTRY_DSN` for error tracking
2. **Application Metrics**: Access `/admin/metrics` for system stats
3. **Database Monitoring**: Use MySQL Performance Schema
4. **Resource Usage**: Monitor with `docker stats` or system tools

### Regular Maintenance Tasks

```bash
# Update application (production)
git pull
docker-compose build --no-cache
docker-compose up -d
./deploy.sh production migrate

# Clean up Docker resources
./deploy.sh production cleanup

# Check SLA breaches
docker-compose exec web flask sla-check

# Generate knowledge articles from resolved tickets
docker-compose exec web flask generate-kb-articles
```

## Troubleshooting

### Common Issues

#### 1. Application won't start
- Check environment variables in `.env`
- Verify database connection
- Check port availability (5000, 3306, 6379)

#### 2. Email integration not working
- Verify Office 365 credentials
- Check firewall for SMTP/IMAP ports (587, 993)
- Ensure modern authentication is enabled in Office 365

#### 3. OAuth authentication failing
- Verify Microsoft App registration
- Check redirect URIs in Azure AD
- Ensure proper tenant configuration

#### 4. High memory usage
- Increase worker processes: modify `gunicorn` command
- Optimize database queries
- Enable Redis for caching

#### 5. Database connection errors
- Check MySQL service status: `sudo systemctl status mysql`
- Verify database credentials
- Check network connectivity

### Debug Mode

Enable debug logging:

```bash
# In .env file
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# Restart application
docker-compose restart web
```

### Performance Optimization

1. **Database Indexing**:
```sql
-- Add indexes for common queries
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
```

2. **Redis Configuration**:
```bash
# In redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

3. **Nginx Tuning**:
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 2048;
client_max_body_size 16M;
```

### Support

For technical support:
- Email: it-support@mlgruppe.de
- Documentation: https://docs.mlgruppe.de/helpdesk
- Issues: https://github.com/mlgruppe/helpdesk/issues

### Backup & Recovery

#### Automated Backups

```bash
# Setup daily backup cron job
sudo crontab -e

# Add line:
0 2 * * * /path/to/helpdesk/deploy.sh production backup
```

#### Disaster Recovery

1. **Database Recovery**:
```bash
# Restore MySQL backup
mysql -u helpdesk -p helpdesk_db < backup_file.sql

# Restore SQLite backup
cp backup_file.db helpdesk.db
```

2. **File Recovery**:
```bash
# Restore uploaded files
tar -xzf uploads_backup.tar.gz -C /app/uploads/
```

3. **Configuration Recovery**:
```bash
# Restore environment configuration
cp .env.backup .env
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS encryption
- [ ] Configure firewall rules
- [ ] Set up regular security updates
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up intrusion detection
- [ ] Regular security scans
- [ ] Backup encryption
- [ ] Access key rotation

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or HAProxy
2. **Database Clustering**: MySQL Master-Slave setup
3. **Redis Clustering**: For high availability
4. **File Storage**: Shared storage or S3-compatible service

### Vertical Scaling

1. **Increase Resources**: CPU, RAM, storage
2. **Database Tuning**: Buffer pool, connections
3. **Application Tuning**: Worker processes, thread pools

This deployment guide ensures a robust, scalable, and maintainable installation of the ML Gruppe Helpdesk system.