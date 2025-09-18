# Gunicorn configuration for trust.chitty.cc deployment

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 4))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Log to stdout/stderr
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'chitty_trust_api'

# Server mechanics
preload_app = True
daemon = False
user = None
group = None
tmp_upload_dir = None

# SSL (for HTTPS)
if os.environ.get('SSL_CERT_PATH'):
    keyfile = os.environ.get('SSL_KEY_PATH')
    certfile = os.environ.get('SSL_CERT_PATH')
    ssl_version = 5  # TLS 1.2+
    ciphers = 'TLSv1.2+HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA'