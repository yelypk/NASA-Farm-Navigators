#!/usr/bin/env bash
set -euo pipefail

# диагностические логи, чтобы в Deploy Logs было видно окружение
echo "[startup] whoami: $(whoami)"
echo "[startup] PWD: $(pwd)"
echo "[startup] PATH: $PATH"

# покажем, что venv существует
if [ -d /opt/venv/bin ]; then
  ls -la /opt/venv/bin | head -n 10 || true
else
  echo "[startup] /opt/venv/bin not found" >&2
fi

# запускаем Python именно из venv
/opt/venv/bin/python -V
exec /opt/venv/bin/python -m uvicorn app.main:app \
  --host 0.0.0.0 --port "${PORT:-8080}" --log-level debug --access-log

