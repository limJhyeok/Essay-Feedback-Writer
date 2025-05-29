#! /usr/bin/env bash

alembic upgrade head

python app/initial_data.py

uvicorn app.main:app --host 0.0.0.0 --port 8000
