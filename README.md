# Legal Contract Assistant

Containerized legal assistant that ingests contracts, builds vector indexes, and answers questions with retrieval-augmented generation. See [instructions](./instructions.md) for course requirements.

[![Service CI](https://github.com/swe-students-fall2025/5-final-charlot/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/REPO_OWNER/REPO_NAME/actions/workflows/backend-ci.yml)
[![Web App CI](https://github.com/swe-students-fall2025/5-final-charlot/actions/workflows/deploy-web.yml/badge.svg)](https://github.com/REPO_OWNER/REPO_NAME/actions/workflows/deploy-web.yml)

## Team Members

- Hyunkyu Park ([hyunkyuu](https://github.com/hyunkyuu))
- Samuel Yang ([SamuelYang24](https://github.com/SamuelYang24))
- Chengqi Li ([lichengqi617](https://github.com/lichengqi617))
- Matthew Zhou ([mzhou3299](https://github.com/mzhou3299))
- Nicole Zhang ([chzzznn](https://github.com/chzzznn))

## Table of Contents

- [About the Project](#about-the-project)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development](#development)

---

## About the Project

**Legal Contract Assistant** is a two-service app that lets users upload contracts, builds embeddings on the CUAD dataset plus user docs, and answers questions with retrieval-augmented generation.

### What It Does

1. **Upload Documents** – PDF/DOCX/TXT uploads from the web UI; contracts are chunked and embedded.
2. **Vector Search** – Embeddings (FAISS + Hugging Face MiniLM) built on CUAD and user uploads.
3. **LLM Reasoning** – Queries are answered with retrieved passages and a reasoning chain.
4. **Chat History** – Authenticated users keep session history; chats can be deleted from the UI.

## System Architecture

```text
┌───────────────────┐      ┌────────────────────────┐      ┌─────────────┐
│ Web App           │─────▶│ ML Service             │      │ MongoDB     │
│ (FastAPI + Jinja) │      │ (FastAPI, LangChain)   │      │             │
│ Port: 9000        │      │ Port: 8000             │      │ Port: 27017 │
│ - Auth/Sessions   │      │ - CUAD ingest          │      │ - Users     │
│ - Upload UI       │      │ - FAISS vector store   │      │ - Sessions  │
│ - Chat + history  │      │ - RAG QA endpoints     │      │ - Messages  │
└───────────────────┘      └────────────────────────┘      └─────────────┘
        │                         │                        │
        └─────────────────────────┴────────────────────────┘
```

## Getting Started

### Prerequisites

- **Docker Desktop** (macOS/Windows) or **Docker Engine + Docker Compose** (Linux)
- **Git**
- (Optional for local dev) **Python 3.13** with **pipenv** if you want to run services outside Docker

### Environment Variables

Copy the provided examples and fill in secrets:

```bash
cp web-app/.env.example web-app/.env
cp service/.env.example service/.env
```

Service `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key for LLM calls | _required_ |
| `VECTOR_DB_PATH` | Where FAISS index is stored | `./data/embeddings/faiss_index` |

Web App `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | Mongo connection string | `mongodb://localhost:27017` (overridden by Compose) |
| `MONGODB_DB` | Database name | `legal_ai` |
| `JWT_SECRET_KEY` | Auth token secret | _required_ |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |

### Running the Application

Start everything:

```bash
docker-compose up --build
```

Access:

- Web UI: [http://localhost:9000](http://localhost:9000)
- ML API: [http://localhost:8000](http://localhost:8000)
- MongoDB: localhost:27017

Stop:

```bash
docker-compose down
```

Stop and remove data:

```bash
docker-compose down -v
```

## Project Structure

```text
.
├── docker-compose.yml           # Orchestrates web-app, service, mongodb
├── service/                     # ML service (FastAPI)
│   ├── main.py                  # CLI: build/run/eval
│   ├── api/                     # HTTP endpoints
│   ├── utils/                   # embeddings, vectorstore, data loader
│   ├── agents/                  # LangChain graph + QA logic
│   ├── prompts/                 # Prompt templates
│   ├── Dockerfile               # Builds the ML container
│   └── .env.example             # Service env template
├── web-app/                     # Frontend + auth (FastAPI + Jinja)
│   ├── app/                     # Routes, templates, static assets
│   ├── tests/                   # Unit tests
│   ├── Dockerfile               # Web app container
│   └── .env.example             # Web env template
└── .github/workflows/           # CI/CD workflows (service + web deploy)
```

## Development

### Run tests locally

```bash
# Web app
cd web-app
pipenv install --dev
pipenv run pytest

# ML service
cd ../service
pipenv install --dev
pipenv run pytest
```

### Useful Docker commands

```bash
# Logs
docker-compose logs -f web-app
docker-compose logs -f service

# Rebuild a single service
docker-compose build web-app
docker-compose build service
```

## Notes / TODO for course admins

- Replace `REPO_OWNER/REPO_NAME` in the badges above with the actual GitHub org/repo.
- Ensure secrets for deploy workflows are set in GitHub Actions (e.g., Docker Hub, DigitalOcean, OpenAI API key).
