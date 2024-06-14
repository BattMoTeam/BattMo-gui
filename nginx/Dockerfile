FROM nginx:1.15.8

# Install Certbot and dependencies
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Remove default Nginx configuration files
RUN rm /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration
COPY nginx.conf /etc/nginx/

# Copy SSL certificate renewal script
COPY renew-certs.sh /renew-certs.sh
RUN chmod +x /renew-certs.sh
