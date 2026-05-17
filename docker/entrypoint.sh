#!/bin/sh
set -e

# Seed the output directory so nginx has something to serve before
# supercronic's first scheduled run at the top of the next hour.
uv run main.py --output /app/dist

exec supervisord -c /etc/supervisord.conf
