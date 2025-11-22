# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env.example .env

# Create model cache directory
RUN mkdir -p /app/model_cache

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_CACHE_DIR=/app/model_cache

# Run the application
CMD ["python", "-m", "src.main"]
