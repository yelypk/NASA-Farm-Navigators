from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import game, plan, tick, events, finance, rasters

app = FastAPI(title="NASA Farm Navigators API", version="0.3.1")

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
def healthz():
    return {"status": "ok", "version": "0.3.1"}

# Static frontend (the built app should be copied into this folder on deploy)
try:
    app.mount("/", StaticFiles(directory=str((__file__[:__file__.rfind('/app/')] + "app/static").replace("\\", "/")), html=True), name="static")
except Exception:
    # If static folder missing in local dev, ignore mount
    pass