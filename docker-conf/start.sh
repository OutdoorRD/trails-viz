#!/bin/bash -e

# Stop running nginx and uWSGI processes
pkill nginx || echo "nginx not running"
pkill uwsgi || echo "uWSGI not running"

# Start uWSGI
/home/nginx/miniconda3/envs/trails-viz-api/bin/uwsgi --ini /home/nginx/trails-viz/trails-viz-api/uwsgi-config.ini &

# Capture the PID of the uWSGI process
UWSGI_PID=$!

# Start nginx
nginx -c /home/nginx/trails-viz/docker-conf/nginx.conf -g 'daemon off;' &

# Capture the PID of the nginx process
NGINX_PID=$!

# Function to handle termination signals
cleanup() {
    echo "Stopping services..."
    kill -TERM "$UWSGI_PID" "$NGINX_PID"
    wait "$UWSGI_PID" "$NGINX_PID"
    echo "Services stopped."
}

# Trap termination signals
trap cleanup SIGINT SIGTERM

# Wait for the services to exit
wait "$UWSGI_PID" "$NGINX_PID"