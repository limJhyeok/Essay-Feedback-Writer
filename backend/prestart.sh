#!/bin/bash

alembic upgrade head

ollama serve &

uvicorn main:app --host 0.0.0.0 --port 8000