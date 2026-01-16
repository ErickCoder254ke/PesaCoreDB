# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire backend directory
COPY backend/ /app/backend/

# Copy the rdbms module (needed by backend)
COPY rdbms/ /app/rdbms/

# Create directory for persistent data (will be mounted as volume in Railway)
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Expose the port (Railway will override with $PORT)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1

# Change to backend directory
WORKDIR /app/backend

# Add healthcheck (Docker will use this, platforms may override)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/health').raise_for_status()" || exit 1

# Railway sets PORT environment variable, default to 8000 for local testing
# Use --timeout-keep-alive for better connection handling
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 75 --log-level info"]
