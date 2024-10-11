FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

# Set the working directory
WORKDIR /app/

# 기본 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean

RUN pip uninstall -y torchvision

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"


# Copy the application code
COPY . .

ENV PYTHONPATH=/app

RUN huggingface-cli download heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF ggml-model-Q5_K_M.gguf --local-dir ./EEVE-Korean-Instruct-10.8B-v1.0-GGUF --local-dir-use-symlinks False

# Ollama 설치
RUN bash -c "$(curl -fsSL https://ollama.com/install.sh)"

# Start the ollama server in the background
RUN ollama serve & \
    # Wait for the ollama server to start (adjust time if necessary)
    sleep 10 && \
    # Create the model after the server is ready
    ollama create EEVE-Korean-10.8B -f ./EEVE-Korean-Instruct-10.8B-v1.0-GGUF/Modelfile

# Expose the port that the app will run on
EXPOSE 8000
