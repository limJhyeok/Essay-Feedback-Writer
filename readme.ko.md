# ChatGPT Clone 프로젝트

**언어 선택 / Language Selection:**

- [🇰🇷 한국어 (Korean)](readme.ko.md)
- [🇺🇸 English](readme.md)

## 기술 스택 및 기능

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com): Python 백엔드 API 구축.
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org/): Python SQL 데이터베이스 상호작용(ORM) 처리.
    - 🔍 [Pydantic](https://docs.pydantic.dev): FastAPI에서 사용하며 데이터 유효성 검사 및 설정 관리.
    - 💾 [PostgreSQL](https://www.postgresql.org): 데이터베이스 사용.
    - 📁 [Adminer](https://www.adminer.org/): 데이터베이스 관리 시스템.
    - 🤖 [Ollama](https://ollama.com/): LLM(EEVE-Korean) 로컬 호스팅.
    - ⛓️ [LangChain](https://www.langchain.com/): LLM 챗봇 구축.
- 🚀 [Svelte](https://svelte.dev/): 프론트엔드.
- 🐋 [Docker Compose](https://www.docker.com): 개발 및 배포 환경.
- 🔒 기본적인 비밀번호 해싱 기능.
- 🔑 JWT (JSON Web Token) 인증.
- 📫 이메일 기반 비밀번호 복구.
- ✅ [Pytest](https://pytest.org): 테스트.
- 📞 [Traefik](https://traefik.io): 리버스 프록시 / 로드 밸런서.
- 🚢 Docker Compose를 사용한 배포 지침, 자동 HTTPS 인증서를 처리하는 프론트엔드 Traefik 프록시 설정.

### 대시보드 로그인

[![API docs](imgs/login.png)](https://github.com/limJhyeok/ChatGPT-Clone)

### 대시보드 비밀번호 복구
[![API docs](imgs/password_recovery.png)](https://github.com/limJhyeok/ChatGPT-Clone)

### 대시보드 채팅
[![API docs](imgs/dashboard_chat.png)](https://github.com/limJhyeok/ChatGPT-Clone)

## 사용법
### 인프라
이 프로젝트는 GPU 클라우드 서비스([paperspace](https://www.paperspace.com/))를 사용하여 개발되었습니다.
- 운영 체제: Ubuntu 22.04
- GPU: Quadro RTX4000(8192MiB)
  - RAG 사용 시 GPU 메모리 부족으로 어려움이 있을 수 있습니다.
- CUDA 버전: 12.6

### .env 파일 설정
루트 폴더에 **.env** 파일을 만들어 주세요.
```
PROJECT_NAME="ChatGPT Clone Project"
STACK_NAME="ChatGPT-Clone-Project"
DOMAIN=localhost

# 백엔드 URL
VITE_SERVER_URL=http://127.0.0.1:8000 # backend(CPU)
VITE_EEVE_SERVER_URL=http://127.0.0.1:9000 # EEVE Korean container(GPU)

# 프론트엔드 URL
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,http://127.0.0.1:5173,https://localhost,https://localhost:5173,https://127.0.0.1:5173"
DOMAIN_PORT="5173"

USE_HASH_ROUTER = "True"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 인증을 위한 secret key 및 알고리즘
SECRET_KEY =
ALGORITHM =

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME =
SMTP_PASSWORD =
EMAILS_FROM_EMAIL = "info@example.com"
EMAILS_FROM_NAME = "ChatGPT Clone Project Information"

# Postgres 설정
## Dev(or Prod) DB
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
## Test DB
TEST_POSTGRES_SERVER=localhost
TEST_POSTGRES_PORT=5432
TEST_POSTGRES_DB=test
TEST_POSTGRES_USER=postgres
TEST_POSTGRES_PASSWORD=changethis

# langsmith 설정
LANGCHAIN_TRACING_V2 = 'true'
LANGCHAIN_API_KEY =
```
- **PROJECT_NAME**: 프로젝트 이름
- **STACK_NAME**: Docker Compose 라벨 및 프로젝트 이름(공백 및 마침표 제외) (이 값은 .env에 설정)
- **SECRET_KEY**: 프로젝트의 보안을 위한 secret key, .env 파일에 저장.
- **SMTP_USERNAME**: 이메일 전송을 위한 SMTP 서버 사용자명.
- **SMTP_PASSWORD**: 이메일 전송을 위한 SMTP 서버 비밀번호.
- **LANGCHAIN_TRACING_V2**: Langsmith를 사용하여 AI 챗봇의 응답을 자세히 추적할지 여부.
- **LANGCHAIN_API_KEY**: Langsmith에서 AI 챗봇 응답을 추적하기 위한 API 키.

### Docker Compose로 컨테이너 실행
```bash
sudo docker-compose up
```
위 명령어를 통해 다음의 컨테이너가 생성됩니다:
- 리버스 프록시(Traefik)
- 데이터베이스(PostgreSQL)
- 백엔드(FastAPI)
- 프론트엔드(Svelte)
- 데이터베이스 관리 시스템(Adminer)

예시)
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

### 테스트 환경에서 Docker Compose 실행

테스트 환경에서 컨테이너를 실행하려면 다음 명령어를 사용하세요:
```bash
sudo docker-compose -f docker-compose.yaml -f docker-compose.override.yaml -f docker-compose.test.yaml up
```
위 명령어를 실행하면 개발(dev) 또는 운영(prod) 환경의 데이터베이스와 격리된 테스트 전용 데이터베이스(test DB)가 실행됩니다.

백엔드와 EEVE에서 테스트를 수행하면, 해당 데이터가 test DB 에 저장됩니다.
테스트 진행 시 데이터 분리를 위해 test DB 를 사용하는 것을 권장합니다.

### CPU-only 환경에서 Docker Compose 실행
GPU가 없는 환경에서 딥러닝 모델인 EEVE-Korean 모델을 실행하는 데에 제약이 있기 때문에, eeve 컨테이너를 제외하고 다른 컨테이너만 실행해야합니다. 이를 위해 다음 명령어를 사용하세요:
```bash
sudo docker compose up --scale eeve=0
```
**주의: EEVE-Korean 모델과 대화할 수 없습니다.**

## 백엔드 개발
백엔드 문서: [backend/readme.md](./backend/readme.ko.md)

## 개발

일반적인 개발 문서: [development.md](./development.ko.md).

이 문서에는 Docker Compose 사용, pre-commit, `.env` 설정 등의 내용이 포함되어 있습니다.

## Acknowledgements
이 레포지토리는 [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)를 기반으로 개발되었습니다. 만약 FastAPI를 이용하실 생각이 있으시면 [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)은 좋은 참고자료가 될 것입니다.
```
@online{full-stack-fastapi-template,
  author    = {fastapi},
  title     = {full-stack-fastapi-template},
  url       = {https://github.com/fastapi/full-stack-fastapi-template},
  year      = {2024},
}
```
