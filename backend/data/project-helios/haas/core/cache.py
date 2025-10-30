"""
Redis Cache Utilities for HaaS Platform
Provides decorators and functions for caching expensive operations.
"""

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional
import redis
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis connection
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    redis_client.ping()
    logger.info(f"✓ Redis connected: {settings.REDIS_URL}")
except Exception as e:
    logger.error(f"✗ Redis connection failed: {e}")
    redis_client = None


def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key based on function arguments.

    Args:
        prefix: Cache key prefix (e.g., 'inmetro', 'tariff')
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: MD5 hash of serialized arguments
    """
    # Serialize arguments to create unique key
    key_data = {"args": args, "kwargs": kwargs}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_result(
    prefix: str, ttl: int = 3600, key_builder: Optional[Callable] = None
) -> Callable:
    """
    Generic cache decorator for any function.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 1 hour)
        key_builder: Optional custom key builder function

    Returns:
        Decorated function with caching

    Example:
        @cache_result(prefix='api', ttl=300)
        def fetch_data(param1, param2):
            return expensive_operation(param1, param2)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip cache if Redis is not available
            if redis_client is None:
                logger.warning(f"Cache miss (Redis unavailable): {func.__name__}")
                return func(*args, **kwargs)

            try:
                # Generate cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = _generate_cache_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = redis_client.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.debug(f"Cache miss: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                redis_client.setex(cache_key, ttl, json.dumps(result, default=str))

                return result

            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                # Fallback to direct execution on cache errors
                return func(*args, **kwargs)

        return wrapper

    return decorator


def cache_inmetro_result(ttl: int = 86400) -> Callable:
    """
    Cache decorator specifically for INMETRO validation results.
    Default TTL: 24 hours (certificates don't change frequently).

    Args:
        ttl: Time to live in seconds (default: 24 hours)

    Returns:
        Decorated function

    Example:
        @cache_inmetro_result(ttl=86400)
        def validate_inverter(cert_id: str) -> dict:
            return inmetro_api.validate(cert_id)
    """
    return cache_result(prefix="inmetro", ttl=ttl)


def cache_bacen_result(ttl: int = 3600) -> Callable:
    """
    Cache decorator specifically for BACEN SGS API results.
    Default TTL: 1 hour (economic data updates frequently).

    Args:
        ttl: Time to live in seconds (default: 1 hour)

    Returns:
        Decorated function

    Example:
        @cache_bacen_result(ttl=3600)
        def get_selic_rate() -> dict:
            return bacen_api.get_selic()
    """
    return cache_result(prefix="bacen", ttl=ttl)


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., 'inmetro:*', 'tariff:CEMIG:*')

    Returns:
        int: Number of keys deleted

    Example:
        # Invalidate all INMETRO caches
        invalidate_cache('inmetro:*')

        # Invalidate specific distributor tariffs
        invalidate_cache('tariff:CEMIG:*')
    """
    if redis_client is None:
        logger.warning("Cannot invalidate cache: Redis unavailable")
        return 0

    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted} cache keys matching '{pattern}'")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return 0


def get_cache_stats() -> dict:
    """
    Get Redis cache statistics.

    Returns:
        dict: Cache statistics (memory usage, keys count, hit rate, etc.)

    Example:
        stats = get_cache_stats()
        print(f"Total keys: {stats['total_keys']}")
        print(f"Memory used: {stats['used_memory_human']}")
    """
    if redis_client is None:
        return {"error": "Redis unavailable"}

    try:
        info = redis_client.info("stats")
        memory_info = redis_client.info("memory")

        # Count keys by prefix
        inmetro_keys = len(redis_client.keys("inmetro:*"))
        tariff_keys = len(redis_client.keys("tariff:*"))
        bacen_keys = len(redis_client.keys("bacen:*"))
        total_keys = redis_client.dbsize()

        return {
            "total_keys": total_keys,
            "inmetro_keys": inmetro_keys,
            "tariff_keys": tariff_keys,
            "bacen_keys": bacen_keys,
            "used_memory": memory_info.get("used_memory", 0),
            "used_memory_human": memory_info.get("used_memory_human", "N/A"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": _calculate_hit_rate(
                info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
            ),
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}


def _calculate_hit_rate(hits: int, misses: int) -> str:
    """Calculate cache hit rate percentage."""
    total = hits + misses
    if total == 0:
        return "0%"
    return f"{(hits / total * 100):.2f}%"


def clear_all_cache() -> int:
    """
    Clear entire cache (use with caution!).

    Returns:
        int: Number of keys deleted

    Warning:
        This will delete ALL keys in the current Redis database.
        Use only in development or with explicit confirmation.
    """
    if redis_client is None:
        logger.warning("Cannot clear cache: Redis unavailable")
        return 0

    try:
        deleted = redis_client.flushdb()
        logger.warning(f"✗ ALL CACHE CLEARED: {deleted} keys deleted")
        return deleted
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return 0


# Example usage patterns for documentation
if __name__ == "__main__":
    # Example 1: Cache INMETRO validation
    @cache_inmetro_result(ttl=86400)
    def validate_inverter_cert(cert_id: str) -> dict:
        """Simulate INMETRO API call (expensive operation)."""
        import time

        time.sleep(2)  # Simulate API latency
        return {
            "cert_id": cert_id,
            "status": "valid",
            "manufacturer": "Example Corp",
            "model": "INV-1000",
        }

    # Example 2: Cache tariff queries
    @cache_tariff_result(ttl=3600)
    def get_distributor_tariff(distributor: str, modality: str) -> dict:
        """Simulate database query for tariff."""
        import time

        time.sleep(1)  # Simulate DB query
        return {
            "distributor": distributor,
            "modality": modality,
            "tariff": 0.85,
            "currency": "BRL",
            "unit": "kWh",
        }

    # Test cache performance
    print("=== Cache Performance Test ===\n")

    # First call (cache miss)
    import time

    start = time.time()
    result1 = validate_inverter_cert("CERT-12345")
    duration1 = time.time() - start
    print(f"1st call (miss): {duration1:.3f}s - {result1}")

    # Second call (cache hit)
    start = time.time()
    result2 = validate_inverter_cert("CERT-12345")
    duration2 = time.time() - start
    print(f"2nd call (hit):  {duration2:.3f}s - {result2}")

    print(f"\n✓ Speedup: {duration1 / duration2:.1f}x faster with cache")

    # Show cache stats
    stats = get_cache_stats()
    print(f"\n=== Cache Statistics ===")
    print(f"Total keys: {stats['total_keys']}")
    print(f"Hit rate: {stats['hit_rate']}")
    print(f"Memory used: {stats['used_memory_human']}")
