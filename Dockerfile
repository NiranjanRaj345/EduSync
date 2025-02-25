# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p app/uploads && chmod 777 app/uploads

# Create logs directory
RUN mkdir -p logs && chmod 777 logs

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PORT=8000

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT run:app
