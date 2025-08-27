import multiprocessing
import os

# Calculate workers based on CPU cores: (2 * CPU cores) + 1
workers = (2 * multiprocessing.cpu_count()) + 1

# Bind to all interfaces on port 8000
bind = "0.0.0.0:8000"

# Worker timeout
timeout = 120

# Worker class
worker_class = "sync"

# Maximum requests per worker before restart (helps prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload application for better performance
preload_app = True

# Logging
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "django_api_gunicorn"

# Worker processes will be restarted after this many requests
worker_connections = 1000
