# Build stage - install dependencies
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN pip install --no-cache-dir pipenv

COPY Pipfile ./

# Install to system and clean up aggressively
RUN pipenv install --system --skip-lock && \
    pip cache purge && \
    rm -rf /root/.cache /tmp/* /var/tmp/* && \
    find /usr/local/lib/python3.13 -name '*.pyc' -delete && \
    find /usr/local/lib/python3.13 -name '__pycache__' -delete

# Runtime stage - smaller final image
FROM python:3.13-slim

WORKDIR /service

# Copy only installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "-m", "api.main"]
