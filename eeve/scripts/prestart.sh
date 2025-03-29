#! /usr/bin/env bash

alembic upgrade head

ollama serve &

uvicorn app.main:app --host 0.0.0.0 --port 9000
