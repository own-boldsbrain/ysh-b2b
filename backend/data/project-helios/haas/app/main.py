"""
HaaS Platform - Homologação como Serviço
API Principal FastAPI para integração com distribuidoras
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    distributors,
    auth,
    webhooks,
    inmetro,
    bacen,
    monitoring,
    documents,
    bacen_realtime,
    journey,
    aneel,
    pgvector,
    pdf_export,
    data_provider,
    data_stream,
    automation,
)
from app.routers.data_stream import start_realtime_updates
from app.services import initialize_agent_runtime

# Prometheus metrics
# from core.metrics import (
#     PrometheusMiddleware,
#     metrics_endpoint,
#     health_endpoint,
#     setup_metrics,
#     cleanup_metrics
# )

# Enhanced OpenAPI documentation
from core.openapi_docs import setup_openapi_enhancement

# Configure logging
settings.setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting HaaS Platform API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Redis URL: {settings.REDIS_URL}")

    # Initialize metrics
    # setup_metrics()
    logger.info("Prometheus metrics initialized")

    # Initialize database tables if needed
    try:
        from app.database import create_tables

        create_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Start background tasks
    start_realtime_updates()
    logger.info("Real-time data simulation started")

    try:
        await initialize_agent_runtime()
        logger.info("Agent integration runtime ready")
    except Exception as exc:
        logger.error("Falha ao inicializar agent runtime: %s", exc)

    yield

    # Shutdown
    # cleanup_metrics()
    logger.info("Prometheus metrics cleaned up")
    logger.info("Shutting down HaaS Platform API")


app = FastAPI(
    title="HaaS Platform API",
    description="API para Homologação como Serviço - " "Integração com Distribuidoras",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# Setup enhanced OpenAPI documentation
setup_openapi_enhancement(app)

# Security middleware for production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure proper hosts in production
    )

# Prometheus metrics middleware (before other middleware)
# app.add_middleware(PrometheusMiddleware)

# Rate Limiting (after Prometheus to track rate limited requests)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(distributors.router, prefix="/distributors", tags=["Distribuidoras"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(inmetro.router, prefix="/api", tags=["INMETRO"])
app.include_router(bacen.router, prefix="/api", tags=["BACEN"])
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(bacen_realtime.router, prefix="/api", tags=["BACEN Realtime"])
app.include_router(journey.router, prefix="/api", tags=["Journey 360º"])
app.include_router(aneel.router, prefix="/api/aneel", tags=["ANEEL"])
app.include_router(pgvector.router, prefix="/api/pgvector", tags=["PGVector"])
app.include_router(pdf_export.router, prefix="/api/pdf", tags=["PDF Export"])
app.include_router(data_provider.router, prefix="/api/data", tags=["Data Provider MCP"])
app.include_router(data_stream.router, prefix="/api/stream", tags=["Data Streaming"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed")
    return {
        "message": "HaaS Platform - Homologação como Serviço",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.is_development else "disabled",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    logger.debug("Health check endpoint accessed")

    # Test database connection
    db_status = "healthy"
    try:
        from app.database import SessionLocal

        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    # Test Redis connection (if configured)
    redis_status = "not_configured"
    try:
        from app.services.redis_service import redis_service

        if redis_service.is_available():
            redis_status = "healthy"
        else:
            redis_status = "unhealthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "service": "haas-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": "2025-10-14T10:00:00Z",
        "checks": {"database": db_status, "redis": redis_status},
    }


# Prometheus metrics endpoint
# app.get("/metrics")(metrics_endpoint)

# Enhanced health check with metrics
# app.get("/health/metrics")(health_endpoint)
