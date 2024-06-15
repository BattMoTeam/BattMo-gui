#!/bin/bash
set -e

# Function to start Nginx in the background
start_nginx() {
    nginx -g 'daemon off;' &
    NGINX_PID=$!
}

# Function to stop the Nginx process
stop_nginx() {
    if [ -n "$NGINX_PID" ]; then
        kill "$NGINX_PID"
    fi
}

# Trap to ensure Nginx is stopped on script exit
trap stop_nginx EXIT

# Start Nginx to serve the challenge files
start_nginx

# Obtain or renew certificates
if [ ! -d "/etc/letsencrypt/live/app.batterymodel.com" ]; then
    certbot certonly --webroot -w /usr/share/nginx/html -d app.batterymodel.com --email lorena.hendrix@sintef.no --agree-tos --non-interactive
else
    certbot renew --webroot -w /usr/share/nginx/html
fi

# Stop the background Nginx process
stop_nginx

# Start Nginx in the foreground
exec nginx -g 'daemon off;'