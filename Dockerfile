# --- Stage 1: fetch the pre-built frontend package ---
FROM node:22-slim AS frontend

WORKDIR /frontend

COPY package.json ./
RUN npm install --omit=dev

RUN mkdir -p /frontend/public && \
    cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. \
        /frontend/public/

# --- Stage 2: application image (backend + nginx) ---
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY . .

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Static frontend build, served by nginx
COPY --from=frontend /frontend/public /app/public

# nginx: proxy /api/* and /r/* to the backend, serve the static SPA otherwise
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]