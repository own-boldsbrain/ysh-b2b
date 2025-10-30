"""
HaaS Platform - Prometheus Metrics Configuration
Configures Prometheus metrics collection for INMETRO API endpoints
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
from functools import wraps


# ==================== Metrics Definitions ====================

# Request metrics
REQUEST_COUNT = Counter(
    "haas_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "haas_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# INMETRO specific metrics
INMETRO_VALIDATION_COUNT = Counter(
    "haas_inmetro_validations_total",
    "Total number of INMETRO validations performed",
    ["status", "equipment_type"],
)

INMETRO_VALIDATION_LATENCY = Histogram(
    "haas_inmetro_validation_duration_seconds",
    "INMETRO validation duration in seconds",
    ["equipment_type"],
)

INMETRO_CACHE_HITS = Counter(
    "haas_inmetro_cache_hits_total",
    "Total number of INMETRO cache hits",
    ["cache_type"],
)

INMETRO_CACHE_MISSES = Counter(
    "haas_inmetro_cache_misses_total",
    "Total number of INMETRO cache misses",
    ["cache_type"],
)

# LLM metrics
LLM_REQUEST_COUNT = Counter(
    "haas_llm_requests_total", "Total number of LLM requests", ["provider", "status"]
)

LLM_REQUEST_LATENCY = Histogram(
    "haas_llm_request_duration_seconds", "LLM request duration in seconds", ["provider"]
)

LLM_TOKEN_USAGE = Counter(
    "haas_llm_tokens_total",
    "Total number of tokens used by LLM",
    ["provider", "direction"],  # direction: input, output
)

# Database metrics
DB_CONNECTION_COUNT = Gauge(
    "haas_db_connections_active", "Number of active database connections"
)

DB_QUERY_LATENCY = Histogram(
    "haas_db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"],
)

# BACEN metrics
BACEN_REQUEST_COUNT = Counter(
    "haas_bacen_requests_total",
    "Total number of BACEN SGS API requests",
    ["endpoint", "status"],
)

BACEN_REQUEST_LATENCY = Histogram(
    "haas_bacen_request_duration_seconds",
    "BACEN SGS API request duration in seconds",
    ["endpoint"],
)


# ==================== Middleware ====================


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics for all endpoints."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract endpoint path (remove path parameters)
        endpoint = request.url.path
        if endpoint.startswith("/api/"):
            # Remove dynamic parts like IDs
            parts = endpoint.split("/")
            if len(parts) > 3 and parts[3].isdigit():
                parts[3] = "{id}"
                endpoint = "/".join(parts)

        response = await call_next(request)

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status_code=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(
            time.time() - start_time
        )

        return response


# ==================== Decorators ====================


def track_inmetro_validation(equipment_type: str):
    """Decorator to track INMETRO validation metrics."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                INMETRO_VALIDATION_COUNT.labels(
                    status="success", equipment_type=equipment_type
                ).inc()
                INMETRO_VALIDATION_LATENCY.labels(
                    equipment_type=equipment_type
                ).observe(time.time() - start_time)
                return result
            except Exception as e:
                INMETRO_VALIDATION_COUNT.labels(
                    status="error", equipment_type=equipment_type
                ).inc()
                raise e

        return wrapper

    return decorator


def track_llm_request(provider: str):
    """Decorator to track LLM request metrics."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                LLM_REQUEST_COUNT.labels(provider=provider, status="success").inc()
                LLM_REQUEST_LATENCY.labels(provider=provider).observe(
                    time.time() - start_time
                )

                # Track token usage if available
                if hasattr(result, "usage"):
                    usage = result.usage
                    if hasattr(usage, "prompt_tokens"):
                        LLM_TOKEN_USAGE.labels(
                            provider=provider, direction="input"
                        ).inc(usage.prompt_tokens)
                    if hasattr(usage, "completion_tokens"):
                        LLM_TOKEN_USAGE.labels(
                            provider=provider, direction="output"
                        ).inc(usage.completion_tokens)

                return result
            except Exception as e:
                LLM_REQUEST_COUNT.labels(provider=provider, status="error").inc()
                raise e

        return wrapper

    return decorator


def track_bacen_request(endpoint: str):
    """Decorator to track BACEN SGS API request metrics."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                BACEN_REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
                BACEN_REQUEST_LATENCY.labels(endpoint=endpoint).observe(
                    time.time() - start_time
                )
                return result
            except Exception as e:
                BACEN_REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
                raise e

        return wrapper

    return decorator


# ==================== Metrics Endpoint ====================


async def metrics_endpoint() -> Response:
    """Endpoint to expose Prometheus metrics."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ==================== Health Check Endpoint ====================


async def health_endpoint() -> dict:
    """Health check endpoint with basic metrics."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "metrics": {
            "total_requests": REQUEST_COUNT._value_sum(),
            "total_validations": INMETRO_VALIDATION_COUNT._value_sum(),
            "cache_hit_ratio": _calculate_cache_hit_ratio(),
        },
    }


def _calculate_cache_hit_ratio() -> float:
    """Calculate cache hit ratio."""
    hits = INMETRO_CACHE_HITS._value_sum()
    misses = INMETRO_CACHE_MISSES._value_sum()
    total = hits + misses
    return hits / total if total > 0 else 0.0


# ==================== Startup/Shutdown Hooks ====================


def setup_metrics():
    """Initialize metrics collection."""
    # This could be extended to collect system metrics periodically
    pass


def cleanup_metrics():
    """Clean up metrics resources."""
    pass
