FROM nginx:1.15.8

COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/nginx.conf
COPY project.conf /etc/nginx/conf.d/
RUN rm /etc/nginx/conf.d/default.conf
