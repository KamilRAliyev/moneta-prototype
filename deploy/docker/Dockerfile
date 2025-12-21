FROM python:3.11-slim

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir "poetry" \
    && poetry --version \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY backend /app/backend/
WORKDIR /app/backend
RUN poetry install --no-interaction --no-ansi

COPY deploy/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
