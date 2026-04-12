import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import CensorateException

from app.api.v1.router import api_router
from app.core.config import Settings
from app.core.database import init_db
from app.core.logger import get_logger
from app.core.exceptions import register_exception_handlers

settings = Settings.get()
logger = get_logger(__name__)

# Parse CORS origins
def parse_list_config(value: str) -> list[str]:
    """Parse comma-separated string to list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

ALLOWED_CORS_ORIGINS = parse_list_config(getattr(settings, "ALLOWED_CORS_ORIGINS", ""))
ALLOWED_HOSTS = parse_list_config(getattr(settings, "ALLOWED_HOSTS", ""))


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom middleware to log HTTP requests."""

    async def dispatch(self, request, call_next):
        logger.info(
            "Request received",
            extra={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers)
            }
        )
        response = await call_next(request)
        logger.info(
            "Request completed",
            extra={
                "status_code": response.status_code,
                "method": request.method,
                "url": str(request.url)
            }
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info("Starting Censorate Management System...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down Censorate Management System...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-native requirement management system",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# Custom rate limit handler matching our error format
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {exc.detail}",
                "status": 429,
                "path": str(request.url.path)
            }
        }
    )


# Configure rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    enabled=getattr(settings, "RATE_LIMIT_ENABLED", True)
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Register exception handlers
register_exception_handlers(app)

# Configure CORS - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host check
allowed_hosts = ALLOWED_HOSTS if ALLOWED_HOSTS else ["localhost", "127.0.0.1", "0.0.0.0"]
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include API routers
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Censorate Management System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8216))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
