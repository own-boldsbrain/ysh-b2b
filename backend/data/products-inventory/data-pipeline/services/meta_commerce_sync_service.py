"""
YSH Meta Commerce Sync Service - Facebook/Instagram Catalog Integration
========================================================================
Syncs extracted solar equipment data to Meta Commerce Platform via Graph API.

Features:
- Product catalog creation and management
- Image upload to Facebook CDN
- Variant management (item_group_id)
- Google Product Category mapping
- Feed generation (CSV, XML/RSS)
- Graph API batch operations
- Compliance with Meta Commerce Platform fields

Meta Commerce Required Fields:
- id, title, description, availability, condition, price
- link, image_link, brand, google_product_category

Author: YSH Platform Team
Version: 2.0.0 (Meta Commerce)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import csv
from io import StringIO
import xml.etree.ElementTree as ET

import psycopg2
from psycopg2.extras import RealDictCursor
import aiohttp
from pydantic import BaseModel, Field, HttpUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaCommerceProduct(BaseModel):
    """
    Pydantic model for Meta Commerce Platform product.

    Based on: https://developers.facebook.com/docs/commerce-platform/catalog/fields
    """

    # Required fields
    id: str  # Unique product ID (SKU)
    title: str  # Max 150 chars
    description: str  # Max 5000 chars
    availability: str  # in stock, out of stock, preorder, available for order
    condition: str  # new, refurbished, used
    price: str  # Format: "9.99 USD"
    link: HttpUrl  # Product URL on your website
    image_link: HttpUrl  # Main product image
    brand: str  # Manufacturer/brand name

    # Highly recommended
    google_product_category: Optional[str] = (
        None  # e.g., "Electronics > Components > Solar Panels"
    )
    product_type: Optional[str] = None  # Your own category

    # Optional but important
    additional_image_link: Optional[List[HttpUrl]] = Field(default_factory=list)
    item_group_id: Optional[str] = None  # For variants
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    pattern: Optional[str] = None

    # Commerce-specific
    sale_price: Optional[str] = None  # Format: "4.99 USD"
    sale_price_effective_date: Optional[str] = None  # ISO 8601

    # Inventory
    inventory: Optional[int] = None
    quantity_to_sell_on_fb: Optional[int] = None

    # Rich content
    rich_text_description: Optional[str] = None  # HTML allowed

    # Additional
    gtin: Optional[str] = None  # UPC/EAN/ISBN
    mpn: Optional[str] = None  # Manufacturer Part Number
    age_group: Optional[str] = (
        None  # adult, all ages, teen, kids, toddler, infant, newborn
    )
    gender: Optional[str] = None  # male, female, unisex

    # Custom labels (for segmentation)
    custom_label_0: Optional[str] = None
    custom_label_1: Optional[str] = None
    custom_label_2: Optional[str] = None
    custom_label_3: Optional[str] = None
    custom_label_4: Optional[str] = None

    # Shipping
    shipping_weight_value: Optional[float] = None
    shipping_weight_unit: Optional[str] = "kg"

    # Facebook-specific
    fb_product_category: Optional[str] = None


class MetaCommerceSyncService:
    """Service for syncing products to Meta Commerce Platform"""

    def __init__(
        self,
        facebook_catalog_id: str,
        facebook_access_token: str,
        postgres_dsn: str,
        base_product_url: str = "https://ysh.solar/products",
        currency: str = "BRL",
        batch_size: int = 100,
    ):
        self.catalog_id = facebook_catalog_id
        self.access_token = facebook_access_token
        self.postgres_dsn = postgres_dsn
        self.base_product_url = base_product_url.rstrip("/")
        self.currency = currency
        self.batch_size = batch_size

        # Meta Graph API endpoint
        self.graph_api_url = "https://graph.facebook.com/v18.0"

        # Google Product Category for Solar Equipment
        self.solar_categories = {
            "module": "Electronics > Components > Solar Panels",
            "inverter": "Electronics > Components > Power Inverters",
            "battery": "Electronics > Components > Batteries",
            "structure": "Hardware > Building Materials > Solar Mounting Systems",
            "cable": "Electronics > Components > Cables",
        }

    def get_pending_products(self) -> List[Dict]:
        """Fetch products from staging table"""
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
        """Update sync status"""
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

    def map_to_meta_commerce(self, raw_product: Dict) -> MetaCommerceProduct:
        """
        Transform extracted product data to Meta Commerce format.
        """
        product_data = json.loads(raw_product["product_data"])
        metadata = product_data.get("metadata", {})

        # Generate SKU
        sku = f"{raw_product['manufacturer'][:3].upper()}-{product_data.get('handle', 'UNK')}"

        # Determine product type for Google category
        product_type = "module"  # default
        title_lower = product_data["title"].lower()
        if "inverter" in title_lower or "inversor" in title_lower:
            product_type = "inverter"
        elif "bateria" in title_lower or "battery" in title_lower:
            product_type = "battery"
        elif "estrutura" in title_lower or "structure" in title_lower:
            product_type = "structure"

        # Price formatting
        price_value = metadata.get("price", 0)
        price_str = f"{price_value:.2f} {self.currency}"

        # Images
        image_urls = [
            img.get("url") for img in product_data.get("images", []) if img.get("url")
        ]
        main_image = (
            image_urls[0] if image_urls else f"{self.base_product_url}/placeholder.jpg"
        )
        additional_images = image_urls[1:5] if len(image_urls) > 1 else []

        # Build Meta Commerce product
        meta_product = MetaCommerceProduct(
            # Required
            id=sku,
            title=product_data["title"][:150],  # Limit to 150 chars
            description=product_data.get("description", "")[:5000],
            availability="in stock",
            condition="new",
            price=price_str,
            link=f"{self.base_product_url}/{product_data['handle']}",
            image_link=main_image,
            brand=raw_product["manufacturer"],
            # Categories
            google_product_category=self.solar_categories.get(product_type),
            product_type=f"Solar Equipment > {product_type.title()}",
            # Additional images
            additional_image_link=additional_images,
            # Specifications
            material="solar-grade",
            # Custom labels for filtering
            custom_label_0=raw_product["manufacturer"],
            custom_label_1=product_type,
            custom_label_2=f"{metadata.get('power_rating_w', 0)}W",
            # Inventory
            inventory=metadata.get("inventory_quantity", 0),
            # Rich description with specs
            rich_text_description=self._build_rich_description(metadata),
            # Technical specs
            mpn=metadata.get("model", ""),
            # Shipping
            shipping_weight_value=metadata.get("weight_kg", 0),
            shipping_weight_unit="kg",
        )

        return meta_product

    def _build_rich_description(self, metadata: Dict) -> str:
        """Build HTML description with technical specs"""
        specs = []

        if metadata.get("power_rating_w"):
            specs.append(
                f"<li><strong>Potência:</strong> {metadata['power_rating_w']} W</li>"
            )
        if metadata.get("voltage_v"):
            specs.append(f"<li><strong>Tensão:</strong> {metadata['voltage_v']} V</li>")
        if metadata.get("efficiency_pct"):
            specs.append(
                f"<li><strong>Eficiência:</strong> {metadata['efficiency_pct']}%</li>"
            )
        if metadata.get("warranty_years"):
            specs.append(
                f"<li><strong>Garantia:</strong> {metadata['warranty_years']} anos</li>"
            )

        if specs:
            return f"""<p>Especificações técnicas:</p><ul>{''.join(specs)}</ul>"""
        return ""

    async def upload_to_meta_catalog(
        self, products: List[MetaCommerceProduct], session: aiohttp.ClientSession
    ) -> Dict[str, int]:
        """
        Upload products to Meta Catalog via Graph API Batch.

        Uses: POST /{catalog-id}/batch
        """
        stats = {"success": 0, "failed": 0}

        # Build batch request
        batch_requests = []
        for product in products:
            batch_requests.append(
                {
                    "method": "UPDATE",
                    "data": product.dict(exclude_none=True, by_alias=True),
                }
            )

        # Send batch to Graph API
        url = f"{self.graph_api_url}/{self.catalog_id}/batch"
        params = {
            "access_token": self.access_token,
            "requests": json.dumps(batch_requests),
        }

        try:
            async with session.post(url, data=params) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    handles = result.get("handles", [])
                    stats["success"] = len([h for h in handles if h])
                    stats["failed"] = len(batch_requests) - stats["success"]
                    logger.info(
                        f"Batch upload: {stats['success']} success, {stats['failed']} failed"
                    )
                else:
                    error_text = await resp.text()
                    logger.error(f"Batch upload failed: {resp.status} - {error_text}")
                    stats["failed"] = len(batch_requests)
        except Exception as e:
            logger.error(f"Error uploading batch: {e}")
            stats["failed"] = len(batch_requests)

        return stats

    def generate_csv_feed(self, products: List[MetaCommerceProduct]) -> str:
        """
        Generate Meta Commerce CSV feed.

        Format: https://developers.facebook.com/docs/commerce-platform/catalog/fields
        """
        output = StringIO()

        # Define CSV columns (Meta Commerce standard)
        fieldnames = [
            "id",
            "title",
            "description",
            "rich_text_description",
            "availability",
            "condition",
            "price",
            "link",
            "image_link",
            "brand",
            "additional_image_link",
            "google_product_category",
            "product_type",
            "sale_price",
            "item_group_id",
            "color",
            "size",
            "material",
            "inventory",
            "custom_label_0",
            "custom_label_1",
            "custom_label_2",
            "shipping_weight_value",
            "shipping_weight_unit",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            row = product.dict(exclude_none=True)

            # Handle array fields
            if row.get("additional_image_link"):
                row["additional_image_link"] = ",".join(row["additional_image_link"])

            writer.writerow({k: row.get(k, "") for k in fieldnames})

        return output.getvalue()

    def generate_xml_feed(self, products: List[MetaCommerceProduct]) -> str:
        """
        Generate Meta Commerce XML/RSS feed.

        Format: https://developers.facebook.com/docs/commerce-platform/catalog/fields
        """
        rss = ET.Element(
            "rss", {"version": "2.0", "xmlns:g": "http://base.google.com/ns/1.0"}
        )

        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "YSH Solar Products"
        ET.SubElement(channel, "link").text = self.base_product_url
        ET.SubElement(channel, "description").text = "Solar Equipment Catalog"

        for product in products:
            item = ET.SubElement(channel, "item")

            # Required fields with g: prefix
            ET.SubElement(item, "g:id").text = product.id
            ET.SubElement(item, "g:title").text = product.title
            ET.SubElement(item, "g:description").text = product.description
            ET.SubElement(item, "g:link").text = str(product.link)
            ET.SubElement(item, "g:image_link").text = str(product.image_link)
            ET.SubElement(item, "g:availability").text = product.availability
            ET.SubElement(item, "g:price").text = product.price
            ET.SubElement(item, "g:brand").text = product.brand
            ET.SubElement(item, "g:condition").text = product.condition

            # Optional fields
            if product.google_product_category:
                ET.SubElement(item, "g:google_product_category").text = (
                    product.google_product_category
                )

            if product.additional_image_link:
                for img_url in product.additional_image_link:
                    ET.SubElement(item, "additional_image_link").text = str(img_url)

            if product.item_group_id:
                ET.SubElement(item, "g:item_group_id").text = product.item_group_id

        return ET.tostring(rss, encoding="unicode")

    async def sync_batch(self, products: List[Dict]) -> Dict[str, int]:
        """Main sync logic"""
        stats = {"success": 0, "failed": 0}

        # Map to Meta Commerce format
        meta_products = []
        for product in products:
            try:
                meta_product = self.map_to_meta_commerce(product)
                meta_products.append(meta_product)
            except Exception as e:
                logger.error(f"Error mapping {product['title']}: {e}")
                self.mark_sync_status(product["id"], "failed", str(e))
                stats["failed"] += 1

        if not meta_products:
            return stats

        # Upload via Graph API
        async with aiohttp.ClientSession() as session:
            upload_stats = await self.upload_to_meta_catalog(meta_products, session)
            stats["success"] += upload_stats["success"]
            stats["failed"] += upload_stats["failed"]

        # Mark successful products
        for product in products:
            if stats["success"] > 0:
                self.mark_sync_status(product["id"], "synced")

        return stats

    async def run_sync(self) -> Dict[str, int]:
        """Main entry point"""
        logger.info("Starting Meta Commerce sync...")

        products = self.get_pending_products()

        if not products:
            logger.info("No pending products")
            return {"success": 0, "failed": 0}

        logger.info(f"Syncing {len(products)} products to Meta Commerce")

        stats = await self.sync_batch(products)

        logger.info(f"Meta Commerce sync complete: {stats}")

        return stats


# ============================================================================
# CLI
# ============================================================================


async def main():
    """CLI entry point"""
    import os

    service = MetaCommerceSyncService(
        facebook_catalog_id=os.getenv("FACEBOOK_CATALOG_ID"),
        facebook_access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
        postgres_dsn=os.getenv("DATABASE_URL"),
        base_product_url=os.getenv("BASE_PRODUCT_URL", "https://ysh.solar/products"),
        currency=os.getenv("CURRENCY", "BRL"),
    )

    stats = await service.run_sync()

    print("\n" + "=" * 60)
    print("META COMMERCE SYNC REPORT")
    print("=" * 60)
    print(f"✓ Successfully synced: {stats['success']}")
    print(f"✗ Failed: {stats['failed']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
