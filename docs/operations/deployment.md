# HostelFlow Local Production Deployment Guide

Follow this guide to deploy the HostelFlow Flask application in a production-like environment.

## 1. Production Configuration Constraints
Before starting the application, configure your environment variables:
1. Ensure `FLASK_ENV=production` is set in your `.env`.
2. Generate a secure random value for `SECRET_KEY`. **Development placeholder values are strictly rejected.**
3. Verify that `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` point to your production database server.

---

## 2. Running with Gunicorn / Waitress WSGI
To execute the application, do not use the built-in Flask development server (`run.py`). Instead, run a production WSGI server.

### On Linux / macOS (Gunicorn)
Install Gunicorn and run the app factory:
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 "app:create_app('production')"
```

### On Windows (Waitress)
Install Waitress and start the app factory runner:
```bash
pip install waitress
waitress-serve --port=8000 "app:create_app('production')"
```

---

## 3. Reverse Proxy Configuration (Nginx)
Configure Nginx to proxy traffic to your WSGI server and propagate request headers (e.g. `X-Request-ID` and client IPs):
```nginx
server {
    listen 80;
    server_name hostelflow.university.edu;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
    }
}
```
