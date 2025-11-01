# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static/uploads static/outputs static/temp

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port (Render will set PORT environment variable)
EXPOSE 10000

# Run the application with gunicorn
# Render automatically sets PORT, but we need to use $PORT or default to 10000
CMD gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 600 --worker-class sync app:app

