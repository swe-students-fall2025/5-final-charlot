FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /service

# Copy only requirements first for better caching
COPY Pipfile ./

# Install dependencies one by one to reduce memory peaks
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --skip-lock && \
    pip cache purge

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "-m", "api.main"]
