#!/bin/bash
set -e

export PORT="${PORT:-80}"

envsubst '${PORT}' \
    < /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

uvicorn main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

wait -n "$BACKEND_PID" "$NGINX_PID"
EXIT_CODE=$?

kill "$BACKEND_PID" "$NGINX_PID" 2>/dev/null || true
exit "$EXIT_CODE"