"""
Dagster Pipelines para YSH Solar B2B
Sistema de captura automática de imagens de produtos
"""

from .image_capture import daily_manufacturer_scrape, weekly_catalog_update

__all__ = [
    "daily_manufacturer_scrape",
    "weekly_catalog_update",
]
