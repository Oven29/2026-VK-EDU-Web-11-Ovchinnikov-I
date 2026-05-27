# Gunicorn configuration for running application.wsgi
bind = "127.0.0.1:8000"
workers = 2

# To run: gunicorn -c config/gunicorn.conf.py application.wsgi:application
