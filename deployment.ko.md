# Essay Feedback Writer Project - Deployment

**언어 선택 / Language Selection:**

<p align="left">
    한국어&nbsp ｜ &nbsp<a href="deployment.md">English</a>&nbsp
</p>

이 프로젝트는 외부 통신 및 HTTPS 인증서를 처리하기 위해 **Traefik 프록시**가 설정되어 있어야 합니다.

또한 CI/CD(지속적 통합 및 지속적 배포) 시스템을 사용하여 자동 배포할 수 있으며, GitHub Actions 설정이 이미 포함돼 있습니다.

하지만 먼저 몇 가지 설정이 필요합니다. 🤓

## 준비 단계

* 사용할 **원격 서버**를 준비하세요.
* 도메인의 **DNS 레코드**를 서버의 IP로 설정하세요.
* 도메인에 대한 **와일드카드 서브도메인**을 설정하세요. 예: `*.{DOMAIN}`
  예시로 `dashboard.{DOMAIN}`, `api.{DOMAIN}`, `traefik.{DOMAIN}`, `adminer.{DOMAIN}`,
  또는 스테이징용 `dashboard.staging.{DOMAIN}`, `adminer.staging.{DOMAIN}` 등이 가능합니다.
* 원격 서버에 [Docker 엔진](https://docs.docker.com/engine/install/)을 설치하고 설정하세요.

## 공개 Traefik 설정

Traefik 프록시는 외부 요청 및 HTTPS 인증서를 처리합니다.

이 작업은 한 번만 수행하면 됩니다.

### Traefik Docker Compose 설정

* Traefik 설정 파일을 저장할 원격 디렉토리를 생성하세요:

```bash
mkdir -p /root/code/traefik-public/
```

* Traefik Docker Compose 파일을 원격 서버로 복사:

```bash
rsync -a docker-compose.traefik.yml root@your-server.example.com:/root/code/traefik-public/
```

### Traefik 전용 Docker 네트워크 생성

다른 서비스들과 통신하기 위해 `traefik-public`이라는 Docker 네트워크가 필요합니다:

```bash
docker network create traefik-public
```

### Traefik 환경 변수 설정

다음 환경 변수를 원격 서버에 설정하세요:

```bash
export USERNAME=admin
export PASSWORD=changethis
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
echo $HASHED_PASSWORD  # 비밀번호 확인용
export DOMAIN=example-project.example.com
export EMAIL=admin@example.com  # 실제 이메일 사용
```

### Traefik 시작하기

Traefik 설정 파일 위치로 이동한 뒤:

```bash
cd /root/code/traefik-public/
docker compose -f docker-compose.traefik.yml up -d
```

## 프로젝트 배포

이제 Traefik이 설정되었으므로 Docker Compose를 사용해 프로젝트를 배포할 수 있습니다.

⚠️ CI/CD 설정(GitHub Actions)으로 건너뛰고 싶다면 해당 섹션으로 이동하세요.

## 환경 변수 설정

```bash
export ENVIRONMENT=production
export DOMAIN=example-project.example.com
```

기타 예시:

```bash
export PROJECT_NAME="Example Project"
export STACK_NAME="example-project-example-com"
export BACKEND_CORS_ORIGINS="https://dashboard.${DOMAIN}"
export SECRET_KEY="(보안 키 생성 필요)"
export FIRST_SUPERUSER=admin@example.com
export FIRST_SUPERUSER_PASSWORD=changeme
export SMTP_HOST=smtp.example.com
export SMTP_USER=username
export SMTP_PASSWORD=secret
export EMAILS_FROM_EMAIL=noreply@example.com
export POSTGRES_SERVER=db
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=changeme
export POSTGRES_DB=app
```

## GitHub Actions 환경 변수 (자동 배포용)

GitHub Actions에서만 사용하는 변수:

* `LATEST_CHANGES`
* `SMOKESHOW_AUTH_KEY`

### 비밀 키 생성

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

출력된 값을 `SECRET_KEY`나 `FIRST_SUPERUSER_PASSWORD` 등에 사용하세요.


## Docker Compose로 배포

모든 환경 변수를 설정한 후:

```bash
docker compose -f docker-compose.yml up -d
```

`docker-compose.override.yml`은 생략하는 것이 프로덕션 환경에 더 적합합니다.

## 지속적 배포 (CD) – GitHub Actions

GitHub Actions로 자동 배포 설정이 가능합니다. 😎

기본적으로 `staging`, `production` 두 가지 환경이 구성돼 있습니다. 🚀

### GitHub Actions 러너 설치

1. 원격 서버에서 러너 전용 사용자 생성:

```bash
sudo adduser github
sudo usermod -aG docker github
```

2. 해당 사용자로 전환:

```bash
sudo su - github
```

3. GitHub 공식 가이드를 참고하여 [self-hosted runner 설치](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners#adding-a-self-hosted-runner-to-a-repository)

4. 설치 후 서비스로 등록:

```bash
exit  # github 사용자에서 나와서
sudo su  # root로 전환
cd /home/github/actions-runner
./svc.sh install github
./svc.sh start
./svc.sh status
```

### GitHub Secrets 설정

레포지토리에서 다음 secrets들을 설정하세요 ([공식 가이드 참고](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository)):

* `DOMAIN_PRODUCTION`
* `DOMAIN_STAGING`
* `STACK_NAME_PRODUCTION`
* `STACK_NAME_STAGING`
* `EMAILS_FROM_EMAIL`
* `FIRST_SUPERUSER`
* `FIRST_SUPERUSER_PASSWORD`
* `POSTGRES_PASSWORD`
* `SECRET_KEY`
* `LATEST_CHANGES`
* `SMOKESHOW_AUTH_KEY`


## GitHub Actions 배포 워크플로우

`.github/workflows/` 디렉토리에 이미 워크플로우가 구성되어 있습니다:

* `staging`: `main` 브랜치에 push 또는 merge 시 배포
* `production`: 릴리스 생성 시 배포

다른 환경이 필요하다면 이 설정들을 복사해서 수정하면 됩니다.

## URLs

Replace `example-project.example.com` with your domain.

### Main Traefik Dashboard

Traefik UI: `https://traefik.example-project.example.com`

### Production

Frontend: `https://dashboard.example-project.example.com`

Backend API docs: `https://api.example-project.example.com/docs`

Backend API base URL: `https://api.example-project.example.com`

Adminer: `https://adminer.example-project.example.com`

### Staging

Frontend: `https://dashboard.staging.example-project.example.com`

Backend API docs: `https://api.staging.example-project.example.com/docs`

Backend API base URL: `https://api.staging.example-project.example.com`

Adminer: `https://adminer.staging.example-project.example.com`
