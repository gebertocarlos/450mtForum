import os

workers = 4
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
timeout = 120
wsgi_app = "app:create_app()"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
loglevel = "debug" 