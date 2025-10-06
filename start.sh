#!/usr/bin/env bash
set -euo pipefail

echo "[start] PWD: $(pwd)"
echo "[start] Python: $(python --version || true)"
echo "[start] Node: $(node -v 2>/dev/null || echo 'not installed')"

# Если на рантайме ещё нет скопированного билда фронта — соберём и скопируем
if [ -d ../frontend ] && [ ! -d ./app/static ]; then
  echo "[start] Building frontend (fallback)…"
  if command -v npm >/dev/null 2>&1; then
    pushd ../frontend >/dev/null
      if [ -f package-lock.json ]; then npm ci; else npm install; fi
      npm run build
    popd >/dev/null
    mkdir -p ./app/static
    cp -r ../frontend/dist/* ./app/static/ || true
  else
    echo "[start][warn] npm is not available; frontend will not be built at runtime."
  fi
fi

echo "[start] Launching API…"
# ВАЖНО: модуль указываем с полным путём
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8080}"



