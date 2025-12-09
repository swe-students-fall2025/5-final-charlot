# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.
# ⚖️ Name — AI-Powered Legal Research & Case-Finding Assistant

![Backend CI](PLACEHOLDER LINK)
![Frontend CI](PLACEHOLDER LINK)
![NLP Service CI](PLACEHOLDER LINK)
![Docker Build](PLACEHOLDER LINK)

> **Name** is an AI-driven legal assistant that helps users quickly find  
> **relevant case law, precedents, and similar past trials** based on client-entered  
> information or uploaded files (PDF, DOCX, TXT).  
>
> Users interact with the system through a chatbot-style interface, supported by  
> NLP-powered document analysis, case retrieval, and legal reasoning summaries.

---

## 👥 Team Members

| Name | GitHub |
|------|---------|
| **Teammate 1** | https://github.com/SamuelYang24 |
| **Teammate 2** | https://github.com/hyunkyuu |
| **Teammate 3** | https://github.com/mzhou3299 |
| **Teammate 4** | https://github.com/chzzznn |
| **Teammate 5** | https://github.com/lichengqi617 |


---

## System Architecture Overview

LexiAssist is composed of four coordinated subsystems:

1. **Frontend Web App**  
   - Chat UI, file upload, case display  
   - Built with React/Vite (or Vue)  
2. **Backend API**  
   - Authentication, routing, user management  
   - Communication between frontend + NLP service  
3. **NLP Case-Matching Engine**  
   - Extracts facts, builds embeddings, retrieves similar past cases  
   - Uses transformer models (Legal-BERT / OpenAI embeddings)  
4. **PostgreSQL Database**  
   - Stores case metadata, embeddings, user queries

All services run via Docker or individually.

---

## DockerHub Images

| Subsystem | DockerHub Link |
|----------|----------------|
| Frontend | PLACEHOLDER LINK |
| Backend | PLACEHOLDER LINK |
| NLP Service | PLACEHOLDER LINK |
| Database | PLACEHOLDER LINK |

---

## Features

- AI chatbot for client-specific legal Q&A  
- File upload (PDF, TXT, DOCX) with automatic text extraction  
- Embedding-based precedent discovery  
- Relevance-ranked case summaries  
- Secure credential handling via `.env` files  
- Full Docker Compose setup  
- Continuous integration for every subsystem  

---

# Developer Setup  
*Works on macOS, Windows, and Linux*


