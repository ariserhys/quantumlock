"""
FastAPI Main Application

REST API for QuantumLock password generation and analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.config import settings

# Version and metadata
VERSION = settings.app_version
TITLE = f"{settings.app_name} API"
DESCRIPTION = """
### 🔐 Advanced Password Security API

Generate strong passwords, analyze strength, check breaches, and more.

## Features

* **Password & Passphrase generation**: Guarantee to generate the password with CSPRNG 
* 🎲 **Password Generator**: CSPRNG-based generation with custom policies
* 🔤 **Passphrase Generator**: Diceware & BIP39 word lists
* 🔍 **Strength Analyzer**: zxcvbn scoring & entropy calculation
* ⚠️ **Breach Checker**: HaveIBeenPwned integration (k-anonymity)
* 🔐 **TOTP Generator**: 2FA codes with QR export
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    # Startup
    print(f"🚀 Starting {TITLE} v{VERSION}")
    print(f"📍 API Docs: http://{settings.api_host}:{settings.api_port}/docs")
    yield
    # Shutdown
    print(f"⏹️  Shutting down {TITLE}")


# Create app
app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": VERSION,
        "app": settings.app_name,
    }


@app.get("/", tags=["System"])
async def root():
    """API root"""
    return {
        "message": f"Welcome to {TITLE}!",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from backend.api.v1.endpoints import generator, analyzer, totp

app.include_router(
    generator.router,
    prefix="/api/v1",
    tags=["Password Generation"],
)

app.include_router(
    analyzer.router,
    prefix="/api/v1",
    tags=["Password Analysis"],
)

app.include_router(
    totp.router,
    prefix="/api/v1/totp",
    tags=["TOTP/2FA"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected errors"""
    print(f"❌ Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload or settings.debug,
    )
