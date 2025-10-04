set -euo pipefail

if [ -f "frontend/package.json" ]; then
  echo "===> Starting FRONTEND (Phaser)"
  cd frontend
  npm ci
  npx http-server -p "${PORT:-3000}" -c-1 .
  exit 0
fi

if [ -f "backend/requirements.txt" ]; then
  echo "===> Starting BACKEND (FastAPI)"
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
  exit 0
fi

echo "No known app found."
exit 1
