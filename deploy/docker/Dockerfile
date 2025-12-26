FROM python:3.11-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir "poetry" \
    && poetry --version \
    && poetry config virtualenvs.create false

WORKDIR /app

# Copy and install backend dependencies
COPY backend /app/backend/
WORKDIR /app/backend
RUN poetry install --no-interaction --no-ansi

# Copy and install frontend dependencies
WORKDIR /app
COPY frontend /app/frontend/
WORKDIR /app/frontend
RUN npm install

# Copy entrypoint script
COPY deploy/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
EXPOSE 5173
ENTRYPOINT ["/entrypoint.sh"]
