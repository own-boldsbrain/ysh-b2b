#!/usr/bin/env python3
"""
Simple test for Data Provider System
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_system():
    """Test basic system functionality."""
    logger.info("Testing Data Provider System...")

    try:
        # Test imports
        from app.services.data_provider_service import DataProviderService

        logger.info("✓ Imports successful")

        # Test service creation
        service = DataProviderService()
        logger.info("✓ Service created")

        # Test basic query
        logger.info("Testing query_data...")
        result = await service.query_data("bacen", limit=1)
        logger.info(f"✓ Query successful: {len(result.get('records', []))} records")

        # Test cache
        logger.info("Testing get_cache_stats...")
        cache_stats = await service.get_cache_stats()
        logger.info(f"✓ Cache stats: {bool(cache_stats)}")

        # Test alerts
        logger.info("Testing get_active_alerts...")
        alerts = await service.get_active_alerts()
        logger.info(f"✓ Active alerts: {len(alerts)}")

        logger.info("All tests passed! 🎉")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(test_system())
