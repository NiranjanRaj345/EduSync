import os
import multiprocessing

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'uvicorn.workers.UvicornWorker'  # For async support
worker_connections = 1000
timeout = 120
keepalive = 5

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
