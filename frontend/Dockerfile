FROM nginx:1.27-alpine
COPY frontend /usr/share/nginx/html
COPY frontend/10-config.sh /docker-entrypoint.d/10-config.sh
RUN chmod +x /docker-entrypoint.d/10-config.sh
EXPOSE 80
