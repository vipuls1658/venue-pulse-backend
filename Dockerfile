# Single-stage image for the ASGI backend (Django + Channels via daphne).
FROM python:3.12-slim

# Faster, quieter, unbuffered Python in containers.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# mysqlclient needs a compiler + the MySQL client headers to build; netcat lets
# the entrypoint wait for the database before migrating.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first so the layer caches across code changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Created at import-time by settings too, but make it explicit for the image.
RUN mkdir -p logs

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
# Serve over ASGI so HTTP and the websocket share one process.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
