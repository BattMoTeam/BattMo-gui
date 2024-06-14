#!/bin/bash

# Run Certbot to obtain or renew certificates
certbot --nginx --non-interactive --agree-tos -d app.batterymodel.com

# Reload Nginx configuration to apply new certificates
nginx -s reload