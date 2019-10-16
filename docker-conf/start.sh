#!/bin/bash -e
uwsgi /app/uwsgi-config.ini &
nginx -g 'daemon off;'
