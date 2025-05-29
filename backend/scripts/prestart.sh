#! /usr/bin/env bash

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000

python app/initial_data.py
