set -euo pipefail

echo "[startup] whoami: $(whoami)"
echo "[startup] PWD: $(pwd)"
echo "[startup] PATH: $PATH"
echo "[startup] PORT: ${PORT:-8080}"
python -V

# Бутстрап БД — только если есть URL
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "[startup] bootstrap DB via app/db.py"
  # db.py сам решит, что делать (guard сверху)
  python app/db.py || echo "[startup] db bootstrap returned non-zero; continuing"
else
  echo "[startup] DATABASE_URL empty; skip DB bootstrap"
fi

# Запуск API
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
