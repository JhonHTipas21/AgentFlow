"""
AgentFlow — Production-Ready Multi-Agent System with Claude API

Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import logging.config

from app.models import Base
from app.database import engine, get_db
from app.config import settings
from app.logging_config import LOGGING_CONFIG
from app.middleware.auth import create_access_token
from app.routers import agents, workflows, tools

# ─── Setup Logging ───────────────────────────────────────
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables initialized")
    yield
    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


# ─── FastAPI App ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-Ready Multi-Agent System with Claude API.\n\n"
        "AgentFlow orchestrates multiple AI agents that collaborate using Claude "
        "to automate complex enterprise workflows end-to-end."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS Middleware ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ─── Include Routers ─────────────────────────────────────
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(tools.router, prefix="/tools", tags=["Tools"])

# ═══════════════════════════════════════════════════════
# HEALTH & SYSTEM ENDPOINTS
# ═══════════════════════════════════════════════════════

@app.get("/health", tags=["System"])
def health_check():
    """Health check — always returns OK if the service is running."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/ready", tags=["System"])
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check — verifies database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True, "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/info", tags=["System"])
def app_info():
    """Application information and feature flags."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "features": {
            "webhooks": settings.ENABLE_WEBHOOKS,
            "monitoring": settings.ENABLE_MONITORING,
        },
    }


# ─── Auth Token (Development) ───────────────────────────
@app.post("/token", tags=["Auth"])
def get_token():
    """
    Generate a development JWT token.

    In production, replace with proper user authentication.
    """
    token = create_access_token({"sub": "developer", "role": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# ═══════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with structured response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )

# ─── Serve Frontend (Catch-all must be last) ────────────
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    logger.info(f"Serving frontend from {frontend_dist}")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{catchall:path}", include_in_schema=False)
    def serve_frontend(catchall: str):
        file_path = os.path.join(frontend_dist, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
            
        return JSONResponse(status_code=404, content={"detail": "Frontend build not found"})


# ─── Run directly ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
