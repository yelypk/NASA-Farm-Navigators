from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import game, plan, tick, events, finance, rasters
from .db import engine, get_db, ensure_db  # <- импорт = «запуск db.py»

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при старте — один раз
    await ensure_db()          # упадём сразу, если URL/SSL/доступ не ок
    yield
    await engine.dispose()     # корректно закрыть пул на остановке

app = FastAPI(title="API", lifespan=lifespan)


# CORS: allow same-origin by default; enable all in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(game.router, prefix="")
app.include_router(plan.router, prefix="")
app.include_router(tick.router, prefix="")
app.include_router(events.router, prefix="")
app.include_router(finance.router, prefix="")
app.include_router(rasters.router, prefix="")

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/readyz")
async def readyz(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"db": "ok"}

# Static frontend (the built app should be copied into this folder on deploy)
try:
    app.mount("/", StaticFiles(directory=str((__file__[:__file__.rfind('/app/')] + "app/static").replace("\\", "/")), html=True), name="static")
except Exception:
    # If static folder missing in local dev, ignore mount
    pass







