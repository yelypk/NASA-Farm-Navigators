from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import regions, simulate, summary
from .services.db import init_db

app = FastAPI(title="Farm Navigators API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _init_db():
    await init_db()

app.include_router(regions.router)
app.include_router(simulate.router)
app.include_router(summary.router)

@app.get("/")
async def root():
    return {"ok": True, "service": "Farm Navigators API"}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Farm Navigators API")

@app.get("/")
def health():
    return {"ok": True, "service": "Farm Navigators API"}
