import os
import multiprocessing

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', 2))  # Reduced for free tier
worker_class = 'sync'  # Standard synchronous worker
worker_connections = 100  # Reduced for free tier
timeout = 60  # Reduced timeout
keepalive = 2  # Reduced keepalive

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# SSL (if needed)
keyfile = None
certfile = None

# Process naming
proc_name = 'edusync'
