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

# Copy data directory if it exists (for initial data)
COPY data/ /app/data/ 2>/dev/null || mkdir -p /app/data

# Create directory for persistent data
RUN mkdir -p /app/data

# Expose the port (Railway will override with $PORT)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Change to backend directory and start the server
WORKDIR /app/backend

# Railway sets PORT environment variable, default to 8000 for local testing
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
