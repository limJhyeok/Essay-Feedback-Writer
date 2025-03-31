# ChatGPT Clone Project

**언어 선택 / Language Selection:**

- [🇰🇷 한국어 (Korean)](readme.ko.md)
- [🇺🇸 English](readme.md)

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org/) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev) used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
    - 📁 [Adminer](https://www.adminer.org/) as the Database Management System
    - 🤖 [Ollama](https://ollama.com/) as the local hosting server for LLM(EEVE-Korean)
    - ⛓️ [LangChain](https://www.langchain.com/) to build LLM chat bot
- 🚀 [Svelte](https://svelte.dev/) for the frontend
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.

### Dashboard Login

[![API docs](imgs/login.png)](https://github.com/limJhyeok/ChatGPT-Clone)

### Dashboard password recovery
[![API docs](imgs/password_recovery.png)](https://github.com/limJhyeok/ChatGPT-Clone)

### Dashboard Chat
[![API docs](imgs/dashboard_chat.png)](https://github.com/limJhyeok/ChatGPT-Clone)

## How to use it
### Infra
I developed this project using the GPU cloud service([paperspace](https://www.paperspace.com/))
- OS: Ubuntu 22.04
- GPU: Quadro RTX4000(8192MiB)
  - It could be difficult to use RAG because of out of memory in GPU.
- CUDA version: 12.6

### .env file setting
please make the **.env** file in the root folder
```
PROJECT_NAME="ChatGPT Clone Project"
STACK_NAME="ChatGPT-Clone-Project"
DOMAIN=localhost

# backend url
VITE_SERVER_URL=http://127.0.0.1:8000
VITE_EEVE_SERVER_URL=http://127.0.0.1:9000

# frontend url
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,http://127.0.0.1:5173,https://localhost,https://localhost:5173,https://127.0.0.1:5173"
DOMAIN_PORT="5173"

USE_HASH_ROUTER = "True"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# secret key and algorithm for auth
SECRET_KEY =
ALGORITHM =

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME =
SMTP_PASSWORD =
EMAILS_FROM_EMAIL = "info@example.com"
EMAILS_FROM_NAME = "ChatGPT Clone Project Information"

# Postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

# langsmith
LANGCHAIN_TRACING_V2 = 'true'
LANGCHAIN_API_KEY =
```
- **PROJECT_NAME**:  The name of the project
- **STACK_NAME**: The name of the stack used for Docker Compose labels and project name (no spaces, no periods) (in .env).
- **SECRET_KEY**: The secret key for the project, used for security, stored in .env.
- **SMTP_USERNAME**: The SMTP server user to send emails.
- **SMTP_PASSWORD**: The SMTP server password to send emails.
- **LANGCHAIN_TRACING_V2**: Where to use Langsmith to tracing AI chat bot's response in detail.
- **LANGCHAIN_API_KEY**: API Key to tracing AI chat bot's response in Langsmith.

### Execute Containers using docker compsoe
```bash
sudo docker-compose up
```
it will make the containeres
- reverse proxy(Traefik)
- Database(PostgreSQL)
- backend(FastAPI)
- frontend(Svelte)
- Database Management System(Adminer)

for example)
```bash
[+] Building 0.0s (0/0)                                                                                                                                                               docker:default
[+] Running 5/0
 ✔ Container chatgpt-clone-proxy-1    Created                                                                                                                                                   0.0s
 ✔ Container chatgpt-clone-db-1       Created                                                                                                                                                   0.0s
 ✔ Container backend                  Created                                                                                                                                                   0.0s
 ✔ Container frontend                 Created                                                                                                                                                   0.0s
 ✔ Container chatgpt-clone-adminer-1  Created                                                                                                                                                   0.0s
Attaching to backend, chatgpt-clone-adminer-1, chatgpt-clone-db-1, chatgpt-clone-proxy-1, frontend
```

### Excute Containers using docker compose in test environment

To run containers in the test environment, use the following command:
```bash
sudo docker-compose -f docker-compose.yaml -f docker-compose.override.yaml -f docker-compose.test.yaml up
```

Running this command will start a **test database (test DB)** that is **isolated** from the development (dev) and production (prod) databases.

When running tests in the **backend** or **eeve**, all test-related data will be stored in the **test DB**.
To ensure data separation during testing, it is strongly recommended to use the **test DB**.

## Backend Development
Backend docs: [backend/readme.md](./backend/readme.md)

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, pre-commit, `.env` configurations, etc.

## Acknowledgements
This repository is built upon [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template). If you want to use FastAPI, that will be good reference or starting point.
```
@online{full-stack-fastapi-template,
  author    = {fastapi},
  title     = {full-stack-fastapi-template},
  url       = {https://github.com/fastapi/full-stack-fastapi-template},
  year      = {2024},
}
```
