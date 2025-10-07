# NASA-Farm-Navigators

A small **FastAPI (Python 3.12)** backend + **Phaser / Vite (Node 20)** frontend.  
In production the backend serves the compiled SPA from `backend/app/static/` (or directly from `frontend/dist` when running locally).

---

## Project layout

```
backend/                  # Server (FastAPI, SQLAlchemy)
  app/
    main.py               # FastAPI entrypoint + SPA serving
    static/               # Production-ready SPA build lives here
  requirements.txt
frontend/                 # Client (Vite + Phaser)
  public/                 # Static files copied to the root of dist
  src/                    # JS sources
  package.json
```

Key endpoints (when the server is running):

- `/` – serves the SPA
- `/__debug_frontend` – quick JSON check that the server sees a built SPA
- `/healthz` – health check
- `/docs` – Swagger UI (if not shadowed by SPA routing)

---

## Prerequisites

- **Python 3.12**
- **Node.js 20+** and **npm**
- (Optional) PostgreSQL, or use SQLite for local prototyping

---

## Quick start (local)

1) **Clone & enter**
```bash
git clone <repo-url>
cd <repo-folder>
```

2) **Python deps**
```bash
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS/Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

3) **Build the frontend**
```bash
cd frontend
npm install          # or: npm ci (if package-lock.json exists)
npm run build        # creates frontend/dist
cd ..
```

> The server can serve the SPA from **either** `backend/app/static` **or** `frontend/dist`.  
> To mirror production (recommended), copy the build once:
> ```bash
> mkdir -p backend/app/static
> cp -r frontend/dist/* backend/app/static/
> ```

4) **Run the server**
```bash
# from repo root
python -m uvicorn backend.app.main:app --reload --port 8080
```

Open:
- http://localhost:8080/ → SPA
- http://localhost:8080/__debug_frontend → should show `static_index: true` or `dist_index: true`
- http://localhost:8080/healthz
- http://localhost:8080/docs

---

## Configuration (database)

The app expects a database URL (PostgreSQL recommended). Examples:

- **PostgreSQL (psycopg3)**
  ```
  DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
  ```
- **SQLite (local dev)**
  ```
  DATABASE_URL=sqlite:///./local.db
  ```

Backend drivers (ensure one of these is in `backend/requirements.txt`):
```
psycopg[binary]>=3.1      # modern option
# or
psycopg2-binary>=2.9
```

Also make sure `uvicorn` is installed:
```
fastapi>=0.112
uvicorn[standard]>=0.30
```

---

## Deploying on Railway (two proven setups)

### A) Root Directory = `backend/`  *(simplest to reason about)*
- **Start Command**
  ```
  python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
  ```
- **How the SPA is served**
  - Commit a built SPA to `backend/app/static` (see “Quick start” step 3 + copy).
  - Or add a Railway build step that builds `frontend/` and copies to `backend/app/static/`.

### B) Root Directory = repository root  *(autobuild frontend on deploy)*
Add two files at repo root:

**`nixpacks.toml`**
```toml
[phases.setup]
nixPkgs = ["python312", "nodejs_20"]
```

**`Railway.toml`**
```toml
[build]
builder = "NIXPACKS"
buildCommand = """
set -eux
pip install -r backend/requirements.txt
if [ -d frontend ]; then
  ( cd frontend && (npm ci || npm install) && npm run build )
  mkdir -p backend/app/static
  cp -r frontend/dist/* backend/app/static/
fi
"""

[deploy]
startCommand = "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
healthcheckPath = "/healthz"
restartPolicyType = "ON_FAILURE"
```

> If you keep Railway’s **Custom Start Command** in the UI, it overrides the files above.  
> For repo-root deployments, use the start command shown in the `Railway.toml`.  
> For `backend/` root deployments, use `python -m uvicorn app.main:app ...`.

---

## Common pitfalls

- **`{"detail":"Not Found"}` at `/`**  
  No built SPA is available. Build the frontend (Vite), then either:
  - Copy `frontend/dist/*` to `backend/app/static/`, or
  - Use the repo-root Railway setup to build & copy during deploy.

- **`No module named uvicorn`**  
  Add `uvicorn[standard]` to `backend/requirements.txt` and redeploy.

- **Assets like `/legend_ndvi.png` return 404/422**  
  Put static files in `frontend/public/` so Vite copies them to the root of `dist`.  
  The backend mounts the entire build at `/` via `StaticFiles(..., html=True)`.

- **Railway starts with `bash backend/start.sh` but crashes**  
  If **Root Directory = `backend/`**, don’t prefix the path; start with:
  ```
  python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
  ```
  Or clear the UI start command and rely on `Railway.toml`.

---

## License

TBD. (Add a license file when ready.)

---

If you want a one-liner to rebuild + copy the SPA locally before committing:

```bash
(cd frontend && npm install && npm run build)  && mkdir -p backend/app/static  && rm -rf backend/app/static/*  && cp -r frontend/dist/* backend/app/static/
```
