#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker Desktop first, then run this installer again." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is required. Install the Docker Compose plugin or Docker Desktop." >&2
  exit 1
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env from backend/.env.example"
fi

docker compose up --build -d
cat <<'MSG'

SeniorConnect is starting.
Open http://localhost in your browser.
Default login:
  Email: admin@seniorconnect.local
  Password: Admin123!

To stop the app later, run: docker compose down
MSG
