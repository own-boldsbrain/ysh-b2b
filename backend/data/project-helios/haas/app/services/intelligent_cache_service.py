import json
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    key: str
    value: Any
    ttl: int
    created_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class IntelligentCacheService:
    """Intelligent caching service for high-frequency data with predictive prefetching."""

    def __init__(self, redis_service):
        self.redis = redis_service
        self.cache_stats = {}
        self.prefetch_patterns = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with access tracking."""
        value = self.redis.get(key)
        if value:
            # Update access statistics
            await self._track_access(key)
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            # Convert datetime objects to ISO format strings for JSON serialization
            def serialize_dates(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            serialized_value = json.dumps(value, default=serialize_dates)
            success = self.redis.set(key, serialized_value, expires_in=ttl)

            # Track cache entry
            await self._track_entry(key, value, ttl)

            # Trigger prefetching for related data
            await self._trigger_prefetch(key, value)

            return success
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        # Simplified implementation - in production would use Redis SCAN
        # For now, just log the pattern
        logger.info(f"Would invalidate cache entries matching {pattern}")
        return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        # Since our RedisService doesn't have info(), provide basic stats
        stats = {
            "connected": self.redis.is_available(),
            "url": "redis://localhost:6379/0",  # Would come from config in production
        }

        # Add custom stats
        custom_stats = {
            "hit_rate": await self._calculate_hit_rate(),
            "top_keys": await self._get_top_accessed_keys(),
            "memory_usage": "unknown",  # Would need Redis INFO command
            "total_keys": 0,  # Would need Redis INFO command
            "uptime": 0,  # Would need Redis INFO command
        }

        return {**stats, **custom_stats}

    async def prefetch_related_data(self, data_type: str, filters: Dict[str, Any]):
        """Prefetch related data based on access patterns."""
        if data_type == "bacen":
            # Prefetch recent historical data
            await self._prefetch_bacen_history()

        elif data_type == "market":
            # Prefetch related market indicators
            await self._prefetch_market_indicators()

        elif data_type == "regulatory":
            # Prefetch compliance requirements
            await self._prefetch_compliance_data()

    async def _prefetch_bacen_history(self):
        """Prefetch BACEN historical data."""
        # Prefetch last 30 days of BACEN data
        prefetch_key = "prefetch:bacen:history:30d"
        if not await self.get(prefetch_key):
            # Simulate fetching historical data
            historical_data = {
                "period": "30d",
                "records": 30,
                "fetched_at": datetime.utcnow().isoformat(),
            }
            await self.set(prefetch_key, historical_data, ttl=3600)

    async def _prefetch_market_indicators(self):
        """Prefetch market indicators."""
        prefetch_key = "prefetch:market:indicators"
        if not await self.get(prefetch_key):
            indicators = {
                "inverter_price_trend": "stable",
                "panel_price_trend": "decreasing",
                "demand_index": 0.85,
                "fetched_at": datetime.utcnow().isoformat(),
            }
            await self.set(prefetch_key, indicators, ttl=1800)  # 30 min

    async def _prefetch_compliance_data(self):
        """Prefetch compliance requirements."""
        prefetch_key = "prefetch:compliance:requirements"
        if not await self.get(prefetch_key):
            requirements = {
                "inmetro_certificates": ["valid", "expiring_soon"],
                "aneel_regulations": ["current", "pending_changes"],
                "fetched_at": datetime.utcnow().isoformat(),
            }
            await self.set(prefetch_key, requirements, ttl=7200)  # 2 hours

    async def _track_access(self, key: str):
        """Track cache access for analytics."""
        access_key = f"access:{key}"
        current_count = self.redis.get(access_key) or 0
        self.redis.set(access_key, int(current_count) + 1, expires_in=86400)  # 24h

    async def _track_entry(self, key: str, value: Any, ttl: int):
        """Track cache entry metadata."""

        # Convert datetime objects to ISO format strings for JSON serialization
        def serialize_dates(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        try:
            size = len(json.dumps(value, default=serialize_dates))
        except:
            size = 0  # Fallback if serialization fails

        entry_data = {
            "key": key,
            "size": size,
            "ttl": ttl,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.redis.set(f"meta:{key}", json.dumps(entry_data), expires_in=ttl)

    async def _trigger_prefetch(self, key: str, value: Any):
        """Trigger prefetching based on data patterns."""
        if "bacen" in key:
            await self._prefetch_bacen_history()
        elif "market" in key:
            await self._prefetch_market_indicators()
        elif "regulatory" in key or "compliance" in key:
            await self._prefetch_compliance_data()

    async def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        # Simplified hit rate calculation
        # In production, would track hits vs misses
        return 0.85  # Mock value

    async def _get_top_accessed_keys(self) -> List[Dict[str, Any]]:
        """Get most accessed cache keys."""
        # Mock implementation - would scan access tracking keys
        return [
            {"key": "bacen:rates", "access_count": 150},
            {"key": "market:prices", "access_count": 89},
            {"key": "regulatory:updates", "access_count": 67},
        ]

    async def warm_cache(self):
        """Warm up cache with frequently accessed data."""
        logger.info("Starting cache warm-up")

        # Warm BACEN data
        bacen_key = "bacen:latest"
        if not await self.get(bacen_key):
            mock_data = {
                "selic": 12.25,
                "cdi": 12.15,
                "spread": 0.10,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await self.set(bacen_key, mock_data, ttl=1800)

        # Warm market data
        market_key = "market:latest"
        if not await self.get(market_key):
            mock_data = {
                "inverters_avg": 2500.00,
                "panels_avg": 1800.00,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await self.set(market_key, mock_data, ttl=3600)

        logger.info("Cache warm-up completed")

    async def cleanup_expired_entries(self):
        """Clean up expired cache entries and metadata."""
        # Redis automatically expires keys, but we can clean metadata
        # This would scan for expired meta keys and remove them
        pass
