FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv

WORKDIR /service

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --skip-lock

COPY . .

EXPOSE 8000

CMD ["./run.sh"]
