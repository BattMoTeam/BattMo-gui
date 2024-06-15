#!/bin/bash

# Stop existing containers
docker compose down

# Obtain/renew SSL certificates
certbot certonly --webroot -w /usr/share/nginx/html -d app.batterymodel.com --agree-tos --email lorena.hendrix@sintef.no

# Start containers again
docker compose up -d

# Reload Nginx to apply new certificates
nginx -s reload