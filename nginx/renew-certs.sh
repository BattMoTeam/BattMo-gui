#!/bin/bash

# Run Certbot to obtain or renew certificates
certbot certonly --non-interactive --agree-tos --email lorena.hendrix@sintef.no --webroot -w /usr/share/nginx/html -d app.batterymodel.com


# Reload Nginx configuration to apply new certificates
nginx -s reload