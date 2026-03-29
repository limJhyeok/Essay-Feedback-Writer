# Essay Feedback Writer Project - Development

**언어 선택 / Language Selection:**

<p align="left">
    한국어&nbsp ｜ &nbsp<a href="development.md">English</a>&nbsp
</p>

## Docker Compose 파일과 환경 변수

전체 스택에 적용되는 모든 설정이 포함된 주 `docker-compose.yml` 파일이 있으며, `docker compose`에서 자동으로 사용됩니다.

또한, 개발을 위한 오버라이드 설정을 포함한 `docker-compose.override.yml` 파일이 있습니다. 예를 들어, 소스 코드를 볼륨으로 마운트하는 설정이 포함됩니다. 이는 `docker compose`에서 자동으로 사용되어 `docker-compose.yml` 파일 위에 오버라이드가 적용됩니다.

이 Docker Compose 파일들은 컨테이너에 환경 변수로 주입될 설정을 포함하는 `.env` 파일을 사용합니다.

또한, `docker compose` 명령을 호출하기 전에 스크립트에서 설정된 환경 변수를 사용하는 추가적인 설정들이 포함됩니다.

## .env 파일

`.env` 파일은 모든 설정, 생성된 키와 비밀번호 등을 포함하는 파일입니다.

워크플로에 따라, 프로젝트가 공개된 경우 `.env` 파일을 Git에서 제외하려 할 수 있습니다. 이 경우 CI 도구가 프로젝트를 빌드하거나 배포할 때 이를 얻을 수 있는 방법을 설정해야 합니다.

이를 수행하는 방법 중 하나는 각 환경 변수를 CI/CD 시스템에 추가하고, `docker-compose.yml` 파일을 업데이트하여 `.env` 파일 대신 해당 환경 변수를 읽는 것입니다.

### Pre-commit과 Code linting

해당 프로젝트는 code linting과 포맷팅을 위해 [pre-commit](https://pre-commit.com/)이라는 도구를 사용하고 있습니다.

이 도구는 git에서 커밋을 하기 전에 자동으로 실행됩니다. 이를 통해 코드가 일관되게 포맷팅되도록 보장합니다.

프로젝트의 루트 디렉토리에는 `.pre-commit-config.yaml` 파일이 있어, 해당 파일에서 설정을 찾을 수 있습니다.

#### pre-commit을 자동으로 실행하도록 설치하기

`pre-commit`은 이미 프로젝트의 종속성에 포함되어 있지만, 원하시면 전역으로 설치할 수도 있습니다. [공식 pre-commit 문서](https://pre-commit.com/)를 참조하세요.

또는 `apt` 도구를 사용하여 설치할 수도 있습니다:
```
apt install -y pre-commit
```

`pre-commit` 도구가 설치되고 사용 가능해지면, 이를 로컬 저장소에 "설치"해야 자동으로 각 커밋 전에 실행됩니다.

```bash
pre-commit install
```

이제 커밋을 시도할 때마다 예를 들어:

```bash
git commit
```

...`pre-commit`이 실행되어 커밋할 코드가 검사되고 포맷팅됩니다. 이후에는 코드를 다시 `git add`하여 수정된 파일을 스테이징한 뒤 커밋할 수 있습니다.

#### pre-commit 훅을 수동으로 실행하기

또한 `pre-commit`을 수동으로 모든 파일에 대해 실행할 수 있습니다.

```bash
❯ pre-commit run

check for added large files..........................(no files to check)Skipped
check toml...........................................(no files to check)Skipped
check yaml...........................................(no files to check)Skipped
fix end of files.....................................(no files to check)Skipped
trim trailing whitespace.............................(no files to check)Skipped
ruff.................................................(no files to check)Skipped
ruff-format..........................................(no files to check)Skipped
```

## URLs

생산 또는 스테이징 환경의 URL은 이와 동일한 경로를 사용하지만, 각자의 도메인으로 변경됩니다.

### 개발용 URLs

로컬 개발을 위한 개발 URLs입니다.

- 프론트엔드: http://localhost:5173
- 백엔드: http://localhost:8000/api/
- 자동 인터랙티브 문서 (Swagger UI): http://localhost:8000/docs
- 자동 대체 문서 (ReDoc): http://localhost:8000/redoc
- Adminer: http://localhost:8080
- Traefik UI: http://localhost:8090

## 커스텀 Claude Code 에이전트 & 스킬

이 프로젝트에는 전문화된 워크플로를 위한 커스텀 Claude Code 에이전트와 스킬이 포함되어 있습니다. `.claude/agents/`와 `.claude/skills/`에 위치합니다.

### 에이전트 (`.claude/agents/`)

에이전트는 작업이 설명과 일치할 때 Claude가 자동으로 위임하는 전문화된 서브에이전트입니다.

| 에이전트 | 용도 |
|----------|------|
| `tdd-backend-enforcer` | 모든 백엔드 코드 변경에 대해 엄격한 TDD (Red → Green → Refactor) 적용 |
| `solution-architect` | 요구사항으로부터 시스템 아키텍처 설계 |
| `api-spec-writer` | 요구사항으로부터 OpenAPI 3.0 명세서 작성 |
| `db-architect` | 데이터베이스 아키텍처 설계 및 평가 |
| `db-schema-reviewer` | 프로덕션 준비 상태를 위한 데이터베이스 스키마 감사 |
| `infra-architect` | 인프라, CI/CD, 스케일링 전략 설계 |
| `web-design-evaluator` | 읽기 전용 UX/UI 감사 — 프론트엔드 디자인을 평가하고 `docs/web-design-evaluation.md`에 결과 출력 |
| `frontend-design-fixer` | 평가 보고서를 읽고 우선순위 순서대로 수정 (Blocking → Major → Moderate) |

**웹 디자인 워크플로 예시:**
```
# 1단계: 평가 (docs/web-design-evaluation.md 생성)
"프론트엔드 디자인을 web-design-evaluator 에이전트로 평가해줘"

# 2단계: 평가 결과의 이슈 수정
"docs/web-design-evaluation.md의 디자인 이슈를 고쳐줘"
```

### 스킬 (`.claude/skills/`)

스킬은 `/command-name` 형태로 호출하는 슬래시 커맨드입니다.

| 스킬 | 커맨드 | 용도 |
|------|--------|------|
| `interaction-mode` | `/interaction-mode` | 단계별 확인이 포함된 페어 프로그래밍 워크플로 |
| `frontend-design` | `/frontend-design` | 프로젝트 디자인 컨벤션에 맞춰 프론트엔드 컴포넌트 빌드 또는 수정 |
| `github-commit` | `/github-commit` | Conventional Commits 표준에 맞는 커밋 메시지 생성 |
| `github-issue` | `/github-issue` | 구조화된 GitHub 이슈 생성 |
| `github-pull-request` | `/github-pull-request` | PR 제목 및 설명 생성 |
| `github-workflow` | `/github-workflow` | 이슈 생성부터 PR 머지까지의 전체 워크플로 가이드 |
| `playwright-cli` | `/playwright-cli` | UI 테스트를 위한 브라우저 자동화 |
