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
ENV PYTHONUNBUFFERED=1

# Create a script to initialize and run the application
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
sleep 5\n\
python -c "from app import create_app; create_app().app_context().push()"\n\
echo "Starting application..."\n\
exec gunicorn --bind 0.0.0.0:$PORT --log-level debug run:app\n'\
> /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
