#!/bin/bash -e

# Stop running nginx and uWSGI processes
pkill nginx || echo "nginx not running"
pkill uwsgi || echo "uWSGI not running"

# Start uWSGI in background
/home/nginx/miniconda3/envs/trails-viz-api/bin/uwsgi --ini /home/nginx/trails-viz/trails-viz-api/uwsgi-config.ini

# Start nginx in background
nginx -c /home/nginx/trails-viz/web-server-conf/nginx.conf