FROM nginx:latest

# Remove default Nginx configuration files
RUN rm /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration
COPY nginx.conf /etc/nginx/
COPY project.conf /etc/nginx/conf.d/

# Copy SSL certificate renewal script
COPY renew-certs.sh /renew-certs.sh
RUN chmod +x /renew-certs.sh
