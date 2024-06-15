#!/bin/bash
set -e

# Obtain/renew SSL certificates
certbot certonly --webroot -w /usr/share/nginx/html -d app.batterymodel.com --agree-tos --email lorena.hendrix@sintef.no
# Reload Nginx to apply new certificates
nginx -s reload