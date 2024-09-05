# ChatGPT Clone Project
## Project Overview
### 1. **Project Overview**

- 목적
    1. full-stack AI 개발의 전과정을 익히기 위해 ChatGPT Clone Project 진행
    2. 추후 AI 프로젝트 진행 시 원활히 협업하기 위해
    3. AI 프로젝트에 대한 큰그림을 익히기 위해
    - ChatGPT Clone Project 선정 이유
        - 기획
            - 기획 간소화
                - Clone project를 선정함으로써 기획에 필요한 여러가지 고려사항들 제외
                - 개발 실력 및 (frontend, backend, AI, 배포 및 운영)간의 협업 프로세스를 익히는데에 중점.
                - 추후 다른 AI Project를 진행할 시, 기획 또한 스스로(또는 협업자를 통해) 진행해볼 예정
        - frontend
            - UI 간소화
                - 웹페이지가 별로 없는 ChatGPT 서비스를 채택함으로써 frontend에 너무 많은 중점을 두지 않기로 함
        - backend
            - backend 간소화
                - 저장 데이터 크기 고려
                    - Text(NLP)의 경우 저장 용량이 상대적으로 가벼우므로 이에 대한 처리가 비교적 쉬울 것으로 예상
            - Chat 서비스의 경우 필요한 엔티티가 상대적으로 적을것으로 예상
                - User, Conversation(유저의 Chat 기록들), Chat(개별 Chat), (Token), (Log) 등
        - AI
            - 성공적인 AI 프로젝트
                - ChatGPT의 경우 대중에게 대표적으로 각인된 첫번째 AI 프로젝트 성공사례
            - LLM에 대한 많은 투자 및 연구 진행 중
                - ChatGPT 성공 이후 LLM에 대해 많은 연구가 진행됨에 따라 open source LLM 모델 또한 성능이 좋게 나오고 있음
            - LLM을 이용한 비즈니스 모델 확장 가능성
                - LLM의 경우 Chat bot 뿐 아니라 copilot, LLM OS 등 다양한 서비스에 적용할 수 있기 때문에 추후에도 LLM을 이용한 서비스는 지속적으로 수요가 있을 예정으로 보임
- **Scope**
    - UI 간소화
        - User가 Chat 서비스를 사용하기에 불편을 느끼지 않을 정도로만 UI 설계 및 개발
    - LLM Finetuning X
        - LLM을 Finetuning 하기에 Resource가 부족할 것으로 보임
        - 이를 보완하기 위해 여러 방안 마련 필요(e. g., Tool, RAG 등)
    - 도덕적 책임 방지
        - 개인 프로젝트일지라도 Hallucination, Prompt Injection 등 LLM의 생성 결과로 인해 발생할 수 있는 도덕적 책임을 방지하기 위해 노력할 예정이지만 User에게 명시적으로 LLM의 결과를 믿지 말라는 문구 삽입 필요
## UI
### 현재 Home page
![home page UI in now](frontend/src/assets/home.png)


## Project Setting

1. back 환경변수 설정
    
    ```bash
    touch .env
    ```
    
    ```
    # ~/.env
    
    # front 서버 url
    DEV_FRONTEND_URL=http://127.0.0.1:8000
    
    # database url
    SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"
    
    # 인증 token 만료 시간(분)
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
    SMTP_HOST = "smtp.gmail.com" # SMTP 발송 서버
    SMTP_PORT = 587
    SMTP_USERNAME = "YOUR_EMAIL@gmail.com" # your gmail
    SMTP_PASSWORD = "YOUR_SMTP_PASSWORD"
    ```
    
2. back 서버 구축
    
    a. python 환경 구축
    
    ```bash
    apt install python3.11
    pip install virtualenv
    virtualenv -p /usr/bin/python3.11 {virtualenv_name}
    source {virtualenv_name}/bin/activate
    
    pip install -r requirement.txt
    ```
    
    b. 모델 checkpoint 설치
    
    ```bash
    huggingface-cli download \
      heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF \
      ggml-model-Q5_K_M.gguf \
      --local-dir EEVE-Korean-Instruct-10.8B-v1.0-GGUF \
      --local-dir-use-symlinks False
    ```
    
    c. ollama 설치
    
    ```bash
    bash -c "$(curl -fsSL https://ollama.com/install.sh)"
    ollama serve &
    ollama create EEVE-Korean-10.8B -f EEVE-Korean-Instruct-10.8B-v1.0-GGUF/Modelfile
    ```
    
3. Database 구축
    
    a. alembic 초기 설정
    
    ```bash
    alembic init migrations
    ```
    
    b. alembic 환경파일 수정
    
    `[파일명: projects/alembic.ini]`
    
    ```
    (... 생략 ...)
    sqlalchemy.url =sqlite:///./{db_name}.db
    (... 생략 ...)
    
    ```
    
 
    
    `[파일명: projects/migrations/env.py]`
    
    ```python
    (... 생략 ...)
    import models
    (... 생략 ...)
    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata
    target_metadata =models.Base.metadata
    (... 생략 ...)
    ```
    
    c. 리비전 파일 생성
    
    ```bash
    alembic revision --autogenerate
    ```
    
    d. 리비전 파일 실행
    
    ```bash
    alembic upgrade head
    ```
    
4. front 서버 구축

    a. nvm & nodejs 설치
    
    ```bash
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    source ~/.bashrc
    nvm install 18.18.0
    nvm use 18.18.0
    nvm alias default 18.18.0
    ```
    
    b. frontend 패키지 설치
    
    ```bash
    cd frontend
    npm install
    ```
    

5. front 환경 변수 설정

    ```bash
    # ~/frontend/.env
    # back 서버 url
    VITE_SERVER_URL=http://127.0.0.1:8000
    ```

