#!/usr/bin/env bash
set -euo pipefail

echo "[start] Python: $(python --version || true)"
echo "[start] Node: $(node -v 2>/dev/null || echo 'not installed')"

# Fallback build for local runs (Railway уже собирает на build-фазе)
if [ -d frontend ] && [ ! -d frontend/dist ]; then
  echo "[start] Building frontend (fallback)…"
  if command -v npm >/dev/null 2>&1; then
    pushd frontend >/dev/null
      if [ -f package-lock.json ]; then npm ci; else npm install; fi
      npm run build
    popd >/dev/null
  else
    echo "[start][warn] npm is not available; frontend will not be served."
  fi
fi

echo "[start] Launching API…"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"

