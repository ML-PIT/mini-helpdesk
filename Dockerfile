# Multi-stage build for production
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash helpdesk

# Copy application code
COPY --chown=helpdesk:helpdesk . .

# Create necessary directories
RUN mkdir -p logs uploads instance backups && \
    chown -R helpdesk:helpdesk logs uploads instance backups

# Switch to non-root user
USER helpdesk

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-flask pytest-cov black flake8 mypy

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs uploads instance backups

# Expose port
EXPOSE 5000

# Command for development
CMD ["python", "app.py"]