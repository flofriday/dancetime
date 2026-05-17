# Build stage: compile the tailwind CSS
FROM node:24-alpine AS css-builder
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm install
COPY tailwind.config.js template.css template.html ./
RUN npx tailwindcss -i template.css -o index.css

# Python builder stage: has the C toolchain so dependencies without a
# pre-built wheel for this (python, arch) combo can compile from source.
# The resulting /app/.venv is copied into the slim runtime stage below.
FROM python:3.14-slim AS python-builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Runtime stage: nginx serves /app/dist, supercronic runs the hourly job,
# supervisord keeps both alive.
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System packages: nginx for hosting, supervisor to run multiple processes,
# ca-certificates so the crawler can reach HTTPS sources.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
        supervisor \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Supercronic: cron designed for containers (single process, no daemonization,
# logs to stdout).
ARG SUPERCRONIC_VERSION=0.2.33
RUN curl -fsSLo /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VERSION}/supercronic-linux-amd64" \
    && chmod +x /usr/local/bin/supercronic

WORKDIR /app
RUN mkdir /app/dist

# Bring in the pre-built virtualenv from the builder stage
COPY --from=python-builder /app/.venv /app/.venv
COPY pyproject.toml uv.lock ./

# Application source
COPY *.py *.html *.css *.svg *.png *.csv ./

# Freshly built CSS from the build stage
COPY --from=css-builder /build/index.css ./index.css

# Process & web configs
COPY docker/nginx.conf       /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisord.conf
COPY docker/crontab          /app/crontab
COPY docker/entrypoint.sh    /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
