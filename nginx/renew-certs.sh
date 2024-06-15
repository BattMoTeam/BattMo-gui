#!/bin/bash

# Run Certbot to obtain or renew certificates
certbot certonly --non-interactive --agree-tos --email lorena.hendrix@sintef.no --webroot -w /usr/share/nginx/html -d app.batterymodel.com

# Verify if certificates have been obtained
if [ -f /etc/letsencrypt/live/app.batterymodel.com/fullchain.pem ]; then
  echo "Certificates have been obtained successfully."
else
  echo "Failed to obtain certificates."
  exit 1
fi
# Reload Nginx configuration to apply new certificates
nginx -s reload