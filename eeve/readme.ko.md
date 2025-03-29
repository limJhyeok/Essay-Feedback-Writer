# ChatGPT Clone Project - backend

**언어 선택 / Language Selection:**

- [🇰🇷 한국어 (Korean)](readme.ko.md)
- [🇺🇸 English](readme.md)

## Requirements

* [Docker](https://www.docker.com/)
* [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
* [Poetry](https://python-poetry.org/) - Python 패키지 및 환경 관리

## 로컬 개발

* Docker Compose로 스택을 시작하세요:

```bash
docker compose up -d
```

* 이제 브라우저에서 아래 URL로 접속하여 상호작용할 수 있습니다:

프론트엔드, Docker로 빌드된 경로 기반 처리: http://localhost:5173

백엔드, OpenAPI 기반 JSON 웹 API: http://localhost:8000

자동화된 Swagger UI 문서(백엔드 OpenAPI에서 제공): http://localhost:8000/docs
[![API docs](../imgs/swagger.png)](https://github.com/limJhyeok/ChatGPT-Clone)

Adminer, 데이터베이스 웹 관리: http://localhost:8080
[![API docs](../imgs/adminer.png)](https://github.com/limJhyeok/ChatGPT-Clone)

Traefik UI, 프록시가 처리하는 경로를 확인: http://localhost:8090
[![API docs](../imgs/traefik.png)](https://github.com/limJhyeok/ChatGPT-Clone)

로그를 확인하려면:

```bash
docker compose logs
```

특정 서비스의 로그를 확인하려면 서비스 이름을 추가하세요, 예를 들어:

```bash
docker compose logs backend
```

### 일반적인 워크플로우

기본적으로 의존성은 [Poetry](https://python-poetry.org/)로 관리됩니다. Poetry를 설치한 후 아래 명령어로 의존성을 설치하세요.

`./backend/` 폴더에서 모든 의존성을 설치하려면:

```console
$ poetry install
```

그 후 새로운 환경으로 셸 세션을 시작하려면:

```console
$ poetry shell
```

편집기가 올바른 Python 가상 환경을 사용하고 있는지 확인하세요.

데이터 및 SQL 테이블에 대한 SqlAlchemy 모델은 `./backend/app/models.py`에서 수정하거나 추가할 수 있습니다. API 엔드포인트는 `./backend/app/api/`에, CRUD(Create, Read, Update, Delete) 유틸리티는 `./backend/app/crud.py`에 있습니다.

### pre-commit 설정
1. pre-commit을 설치하세요
```bash
apt install -y pre-commit
```
2. pre-commit을 적용하세요
```bash
pre-commit install
```

## 백엔드 테스트

백엔드를 테스트하려면:

```console
$ bash ./scripts/test.sh
```

테스트는 Pytest로 실행되며, `./backend/app/tests/`에서 테스트를 수정하거나 추가할 수 있습니다.

GitHub Actions를 사용하면 테스트가 자동으로 실행됩니다.

### 테스트 커버리지

테스트를 실행하면 `htmlcov/index.html` 파일이 생성됩니다. 이 파일을 브라우저에서 열어 테스트의 커버리지를 확인할 수 있습니다.

## 마이그레이션

로컬 개발 중에 앱 디렉터리가 컨테이너 내부에서 볼륨으로 마운트되므로 `alembic` 명령어로 마이그레이션을 실행할 수 있습니다. 마이그레이션 코드는 앱 디렉터리에 저장되어 Git 리포지토리에 추가할 수 있습니다.

모델을 변경할 때마다 "revision"을 생성하고 해당 revision으로 데이터베이스를 "upgrade"해야 합니다. 이렇게 해야 데이터베이스 테이블이 업데이트됩니다. 그렇지 않으면 애플리케이션에 오류가 발생할 수 있습니다.

* 백엔드 컨테이너에서 대화형 세션을 시작하려면:

```console
$ docker compose exec backend bash
```

* Alembic은 `./backend/app/models.py`에서 SQLModel 모델을 자동으로 가져오도록 구성되어 있습니다.

* 모델을 변경한 후(예: 열 추가) 컨테이너 내부에서 revision을 생성하려면 예를 들어:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Alembic 디렉터리에서 생성된 파일을 Git 리포지토리에 커밋합니다.

* revision을 생성한 후, 데이터베이스에서 마이그레이션을 실행하려면:

```console
$ alembic upgrade head
```

## 이메일 템플릿

이메일 템플릿은 `./backend/app/email-templates/`에 있습니다. 여기에는 `build`와 `src`라는 두 개의 디렉터리가 있습니다. `src` 디렉터리에는 최종 이메일 템플릿을 만들 때 사용하는 소스 파일이 있고, `build` 디렉터리에는 애플리케이션에서 사용하는 최종 이메일 템플릿이 있습니다.

계속하기 전에 [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml)을 VS Code에 설치했는지 확인하세요.

MJML extension을 설치한 후, `src` 디렉터리에서 새 이메일 템플릿을 생성할 수 있습니다. 새 이메일 템플릿을 생성한 후 `.mjml` 파일을 열고 `Ctrl+Shift+P`로 명령 팔레트를 열고 `MJML: Export to HTML`을 검색하여 실행하세요. 이렇게 하면 `.mjml` 파일이 `.html` 파일로 변환되고, 이제 이를 `build` 디렉터리에 저장할 수 있습니다.
