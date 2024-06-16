#!/bin/bash
set -e

certbot certonly --webroot -w /usr/share/nginx/html -d app.batterymodel.com --email lorena.hendrix@sintef.no --agree-tos --non-interactive


