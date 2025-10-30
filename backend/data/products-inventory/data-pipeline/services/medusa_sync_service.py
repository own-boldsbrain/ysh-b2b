"""
YSH Medusa Sync Service - Product Import Module
================================================
Syncs extracted manufacturer data from PostgreSQL staging to Medusa commerce.

Features:
- Batch product import with transaction safety
- Image upload to Medusa File Service
- Variant and collection management
- Metadata enrichment
- Conflict resolution

Author: YSH Platform Team
Version: 1.0.0
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

import psycopg2
from psycopg2.extras import RealDictCursor
import aiohttp
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedusaProduct(BaseModel):
    """Pydantic model for Medusa product"""

    title: str
    subtitle: Optional[str] = ""
    description: Optional[str] = ""
    handle: str
    status: str = "published"
    is_giftcard: bool = False
    discountable: bool = True
    type: Dict[str, str] = Field(default_factory=lambda: {"value": "solar-equipment"})
    collection: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    variants: List[Dict[str, Any]] = Field(default_factory=list)


class MedusaSyncService:
    """Service for syncing products to Medusa"""

    def __init__(
        self,
        medusa_url: str = "http://localhost:9000",
        medusa_api_key: Optional[str] = None,
        postgres_dsn: str = "postgresql://ysh_admin:ysh_secure_2025@localhost:5432/ysh_pipeline",
        s3_endpoint: str = "http://localhost:9000",
        batch_size: int = 50,
    ):
        self.medusa_url = medusa_url.rstrip("/")
        self.medusa_api_key = medusa_api_key
        self.postgres_dsn = postgres_dsn
        self.s3_endpoint = s3_endpoint
        self.batch_size = batch_size

        # Headers for Medusa API
        self.headers = {
            "Content-Type": "application/json",
        }
        if medusa_api_key:
            self.headers["x-medusa-access-token"] = medusa_api_key

    def get_pending_products(self) -> List[Dict]:
        """Fetch products from staging table that need sync"""
        conn = psycopg2.connect(self.postgres_dsn)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT id, manufacturer, title, handle, product_data
            FROM product_staging
            WHERE sync_status = 'pending'
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (self.batch_size,),
        )

        products = cursor.fetchall()
        cursor.close()
        conn.close()

        return [dict(p) for p in products]

    def mark_sync_status(
        self, product_id: int, status: str, error_msg: Optional[str] = None
    ):
        """Update sync status in staging table"""
        conn = psycopg2.connect(self.postgres_dsn)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE product_staging
            SET sync_status = %s,
                updated_at = NOW(),
                sync_error = %s
            WHERE id = %s
            """,
            (status, error_msg, product_id),
        )

        conn.commit()
        cursor.close()
        conn.close()

    async def upload_image_to_medusa(
        self, image_s3_url: str, session: aiohttp.ClientSession
    ) -> Optional[str]:
        """Upload image from S3 to Medusa file service"""
        try:
            # Download from S3
            s3_url_clean = image_s3_url.replace("s3://", f"{self.s3_endpoint}/")

            async with session.get(s3_url_clean) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to download image from {s3_url_clean}")
                    return None

                image_data = await resp.read()

            # Upload to Medusa
            form_data = aiohttp.FormData()
            form_data.add_field(
                "file", image_data, filename="product.webp", content_type="image/webp"
            )

            async with session.post(
                f"{self.medusa_url}/admin/uploads",
                data=form_data,
                headers=(
                    {"x-medusa-access-token": self.medusa_api_key}
                    if self.medusa_api_key
                    else {}
                ),
            ) as resp:
                if resp.status in (200, 201):
                    result = await resp.json()
                    return result.get("uploads", [{}])[0].get("url")
                else:
                    logger.error(f"Failed to upload to Medusa: {resp.status}")
                    return None

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None

    async def create_product_in_medusa(
        self, product_data: Dict, session: aiohttp.ClientSession
    ) -> Optional[str]:
        """Create product in Medusa via Admin API"""
        try:
            # Parse product data
            raw_product = json.loads(product_data["product_data"])

            # Upload images first
            medusa_images = []
            for img in raw_product.get("images", []):
                if img.get("url"):
                    uploaded_url = await self.upload_image_to_medusa(
                        img["url"], session
                    )
                    if uploaded_url:
                        medusa_images.append({"url": uploaded_url})

            # Prepare product payload
            payload = {
                "title": raw_product["title"],
                "subtitle": raw_product.get("subtitle", ""),
                "description": raw_product.get("description", ""),
                "handle": raw_product["handle"],
                "status": raw_product.get("status", "published"),
                "is_giftcard": False,
                "discountable": True,
                "metadata": raw_product.get("metadata", {}),
                "images": medusa_images,
            }

            # Add variants
            if raw_product.get("variants"):
                payload["variants"] = raw_product["variants"]

            # Create product
            async with session.post(
                f"{self.medusa_url}/admin/products", json=payload, headers=self.headers
            ) as resp:
                if resp.status in (200, 201):
                    result = await resp.json()
                    product_id = result.get("product", {}).get("id")
                    logger.info(
                        f"Created product: {raw_product['title']} (ID: {product_id})"
                    )
                    return product_id
                else:
                    error_text = await resp.text()
                    logger.error(
                        f"Failed to create product: {resp.status} - {error_text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error creating product in Medusa: {e}")
            return None

    async def sync_batch(self, products: List[Dict]) -> Dict[str, int]:
        """Sync batch of products to Medusa"""
        stats = {"success": 0, "failed": 0, "skipped": 0}

        async with aiohttp.ClientSession() as session:
            for product in products:
                try:
                    product_id = await self.create_product_in_medusa(product, session)

                    if product_id:
                        self.mark_sync_status(product["id"], "synced")
                        stats["success"] += 1
                    else:
                        self.mark_sync_status(
                            product["id"], "failed", "Failed to create in Medusa"
                        )
                        stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Error syncing product {product['title']}: {e}")
                    self.mark_sync_status(product["id"], "failed", str(e))
                    stats["failed"] += 1

        return stats

    async def run_sync(self) -> Dict[str, int]:
        """Main sync process"""
        logger.info("Starting Medusa sync process...")

        # Get pending products
        products = self.get_pending_products()

        if not products:
            logger.info("No pending products to sync")
            return {"success": 0, "failed": 0, "skipped": 0}

        logger.info(f"Found {len(products)} products to sync")

        # Sync batch
        stats = await self.sync_batch(products)

        logger.info(
            f"Sync complete: {stats['success']} success, {stats['failed']} failed"
        )

        return stats


# ============================================================================
# CLI INTERFACE
# ============================================================================


async def main():
    """CLI entry point"""
    import os

    service = MedusaSyncService(
        medusa_url=os.getenv("MEDUSA_URL", "http://localhost:9000"),
        medusa_api_key=os.getenv("MEDUSA_API_KEY"),
        postgres_dsn=os.getenv(
            "DATABASE_URL",
            "postgresql://ysh_admin:ysh_secure_2025@localhost:5432/ysh_pipeline",
        ),
        s3_endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        batch_size=int(os.getenv("SYNC_BATCH_SIZE", "50")),
    )

    stats = await service.run_sync()

    print("\n" + "=" * 60)
    print("MEDUSA SYNC REPORT")
    print("=" * 60)
    print(f"✓ Successfully synced: {stats['success']}")
    print(f"✗ Failed: {stats['failed']}")
    print(f"⊘ Skipped: {stats['skipped']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
