#!/usr/bin/env bash
set -euo pipefail

echo "[startup] whoami: $(whoami)"
echo "[startup] PWD: $(pwd)"
echo "[startup] PATH: $PATH"
echo "[startup] PORT: ${PORT:-8080}"

# покажем структуру и наличие конфигов
echo "[startup] tree:"
ls -la || true
echo "[startup] conf contents:"
ls -la conf || echo "[startup] no conf dir"

# venv от Nixpacks
if [ -d /opt/venv/bin ]; then
  echo "[startup] /opt/venv/bin exists"
else
  echo "[startup] /opt/venv/bin NOT found" >&2
fi

# версия python
/opt/venv/bin/python -V

# 1) bootstrap БД (создание схемы + загрузка манифестов)
echo "[startup] bootstrap DB via app/db.py"
# db.py сам читает conf/crops_manifest.json и conf/infrastructure_manifest.json
/opt/venv/bin/python app/db.py

# 2) старт API
echo "[startup] starting uvicorn"
exec /opt/venv/bin/python -m uvicorn app.main:app \
  --host 0.0.0.0 --port "${PORT:-8080}" --log-level debug --access-log
