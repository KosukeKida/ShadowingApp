from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import materials, youtube, pdf, practice, evaluate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings.ensure_directories()
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    description="English Shadowing Practice Application",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio/recordings
app.mount(
    "/static/materials",
    StaticFiles(directory=str(settings.materials_dir)),
    name="materials",
)
app.mount(
    "/static/recordings",
    StaticFiles(directory=str(settings.recordings_dir)),
    name="recordings",
)

# Include routers
app.include_router(materials.router)
app.include_router(youtube.router)
app.include_router(pdf.router)
app.include_router(practice.router)
app.include_router(evaluate.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
