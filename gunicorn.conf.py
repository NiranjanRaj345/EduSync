import multiprocessing

# Server socket
bind = "0.0.0.0:10000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 300
keepalive = 2

# Process naming
proc_name = "edusync"
env = "production"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# SSL
keyfile = None
certfile = None

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Event handlers
def on_starting(server):
    """Log when server starts."""
    server.log.info("Starting EduSync server")

def on_exit(server):
    """Log when server exits."""
    server.log.info("Shutting down EduSync server")

# SSL Configuration
ssl_version = "TLS"
cert_reqs = "CERT_NONE"
