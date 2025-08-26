#!/bin/bash

# ML Gruppe Helpdesk Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Environments: dev, staging, production
# Actions: build, deploy, migrate, backup, logs

set -e

# Configuration
PROJECT_NAME="ml-helpdesk"
DOCKER_REGISTRY="registry.mlgruppe.de"  # Replace with your registry
BACKUP_RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check requirements
check_requirements() {
    log "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    if [[ ! -f .env.${ENV} ]]; then
        error "Environment file .env.${ENV} not found"
    fi
    
    log "Requirements check passed"
}

# Build application
build() {
    log "Building application for ${ENV} environment..."
    
    # Build Docker image
    docker build -t ${PROJECT_NAME}:${ENV} \
        --target production \
        --build-arg BUILD_ENV=${ENV} .
    
    # Tag for registry if not development
    if [[ "${ENV}" != "dev" ]]; then
        docker tag ${PROJECT_NAME}:${ENV} ${DOCKER_REGISTRY}/${PROJECT_NAME}:${ENV}
        docker tag ${PROJECT_NAME}:${ENV} ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
    fi
    
    log "Build completed successfully"
}

# Deploy application
deploy() {
    log "Deploying ${PROJECT_NAME} to ${ENV} environment..."
    
    # Copy environment file
    cp .env.${ENV} .env
    
    # Choose appropriate docker-compose file
    if [[ "${ENV}" == "dev" ]]; then
        COMPOSE_FILE="docker-compose.dev.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    # Pull images if not development
    if [[ "${ENV}" != "dev" ]]; then
        docker-compose -f ${COMPOSE_FILE} pull
    fi
    
    # Stop existing services
    docker-compose -f ${COMPOSE_FILE} down --remove-orphans
    
    # Start services
    docker-compose -f ${COMPOSE_FILE} up -d
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    migrate
    
    # Health check
    log "Performing health check..."
    sleep 5
    
    if curl -f http://localhost:5000/health &> /dev/null; then
        log "Deployment successful! Application is healthy"
    else
        error "Deployment failed - health check failed"
    fi
}

# Run database migrations
migrate() {
    log "Running database migrations..."
    
    # Initialize migration repository if it doesn't exist
    if [[ ! -d "migrations" ]]; then
        docker-compose exec web flask db init
    fi
    
    # Create migration
    docker-compose exec web flask db migrate -m "Auto migration $(date +%Y%m%d_%H%M%S)"
    
    # Apply migrations
    docker-compose exec web flask db upgrade
    
    # Create admin user if it doesn't exist
    docker-compose exec web flask deploy
    
    log "Database migrations completed"
}

# Create database backup
backup() {
    log "Creating database backup..."
    
    BACKUP_DIR="./backups"
    BACKUP_FILE="helpdesk_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p ${BACKUP_DIR}
    
    if [[ "${ENV}" == "dev" ]]; then
        # SQLite backup for development
        docker-compose exec web cp /app/helpdesk_dev.db /app/backups/${BACKUP_FILE%.sql}.db
    else
        # MySQL backup for production
        docker-compose exec mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} helpdesk_db > ${BACKUP_DIR}/${BACKUP_FILE}
    fi
    
    # Compress backup
    gzip ${BACKUP_DIR}/${BACKUP_FILE}
    
    # Clean old backups
    find ${BACKUP_DIR} -name "helpdesk_backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete
    
    log "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.gz"
}

# Show application logs
show_logs() {
    log "Showing application logs..."
    
    if [[ "${ENV}" == "dev" ]]; then
        COMPOSE_FILE="docker-compose.dev.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    docker-compose -f ${COMPOSE_FILE} logs -f --tail=100 web
}

# Cleanup old Docker resources
cleanup() {
    log "Cleaning up Docker resources..."
    
    docker system prune -f
    docker volume prune -f
    docker image prune -f
    
    log "Cleanup completed"
}

# SSL certificate setup
setup_ssl() {
    log "Setting up SSL certificates..."
    
    SSL_DIR="./nginx/ssl"
    mkdir -p ${SSL_DIR}
    
    if [[ ! -f ${SSL_DIR}/cert.pem ]] || [[ ! -f ${SSL_DIR}/key.pem ]]; then
        warning "SSL certificates not found. Creating self-signed certificates for development..."
        warning "For production, please use proper SSL certificates from a CA"
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ${SSL_DIR}/key.pem \
            -out ${SSL_DIR}/cert.pem \
            -subj "/C=DE/ST=NRW/L=City/O=ML Gruppe/OU=IT/CN=helpdesk.mlgruppe.de"
    fi
    
    log "SSL certificates ready"
}

# Monitor application
monitor() {
    log "Starting monitoring dashboard..."
    
    info "Application Status:"
    docker-compose ps
    
    echo ""
    info "Resource Usage:"
    docker stats --no-stream
    
    echo ""
    info "Recent Logs:"
    docker-compose logs --tail=20 web
}

# Main script logic
ENV=${1:-dev}
ACTION=${2:-deploy}

case ${ENV} in
    dev|staging|production)
        ;;
    *)
        error "Invalid environment: ${ENV}. Use dev, staging, or production"
        ;;
esac

case ${ACTION} in
    build)
        check_requirements
        build
        ;;
    deploy)
        check_requirements
        build
        deploy
        ;;
    migrate)
        migrate
        ;;
    backup)
        backup
        ;;
    logs)
        show_logs
        ;;
    ssl)
        setup_ssl
        ;;
    cleanup)
        cleanup
        ;;
    monitor)
        monitor
        ;;
    *)
        error "Invalid action: ${ACTION}. Use build, deploy, migrate, backup, logs, ssl, cleanup, or monitor"
        ;;
esac