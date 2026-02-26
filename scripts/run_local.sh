#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo '.env criado a partir de .env.example. Ajuste as variáveis se necessário.'
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
