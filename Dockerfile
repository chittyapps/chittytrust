# Dockerfile for ChittyOS Score API deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash chitty
RUN chown -R chitty:chitty /app
USER chitty

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PRODUCTION=true

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "real_trust_api:app"]