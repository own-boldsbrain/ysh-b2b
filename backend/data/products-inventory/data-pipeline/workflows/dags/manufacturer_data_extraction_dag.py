"""
YSH Solar Data Pipeline - Manufacturer Data Extraction DAG
===========================================================
High-performance parallel extraction of solar equipment datasheets and images
from manufacturer websites with full compliance and normalization for Medusa commerce.

Stack: Apache Airflow + Crawlee + Playwright + Polars + MinIO + PostgreSQL
Author: YSH Data Engineering Team
Version: 1.0.0
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Default args for all tasks
default_args = {
    "owner": "ysh-data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "email": ["data-alerts@ysh.solar"],
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# Manufacturer configurations (expandable)
MANUFACTURERS = [
    {
        "name": "Jinko Solar",
        "website": "https://www.jinkosolar.com",
        "product_categories": ["modules", "panels"],
        "selectors": {
            "product_list": ".product-item",
            "datasheet": 'a[href*="datasheet"]',
            "images": "img.product-image",
        },
    },
    {
        "name": "Growatt",
        "website": "https://www.growatt.com",
        "product_categories": ["inverters", "batteries"],
        "selectors": {
            "product_list": ".inverter-card",
            "datasheet": "a.download-spec",
            "images": "img.main-product-img",
        },
    },
    {
        "name": "Canadian Solar",
        "website": "https://www.canadiansolar.com",
        "product_categories": ["modules"],
        "selectors": {
            "product_list": ".module-product",
            "datasheet": 'a[href$=".pdf"]',
            "images": "img.product-photo",
        },
    },
    {
        "name": "Solis",
        "website": "https://www.solisinverters.com",
        "product_categories": ["inverters"],
        "selectors": {
            "product_list": ".product-grid-item",
            "datasheet": ".download-datasheet",
            "images": 'img[alt*="inverter"]',
        },
    },
    {
        "name": "Deye",
        "website": "https://www.deyeinverter.com",
        "product_categories": ["inverters", "batteries"],
        "selectors": {
            "product_list": ".product-box",
            "datasheet": "a.tech-spec",
            "images": ".product-image img",
        },
    },
]


def extract_manufacturer_catalog(**context) -> Dict[str, Any]:
    """
    Extract product catalog from manufacturer website using Crawlee + Playwright.
    High-performance async scraping with automatic retry and rate limiting.
    """
    manufacturer = context["dag_run"].conf.get("manufacturer", MANUFACTURERS[0])

    logger.info(f"Starting catalog extraction for {manufacturer['name']}")

    # Import within task to avoid serialization issues
    from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
    from crawlee import Request
    import asyncio

    extracted_products = []

    async def scrape_products(context_obj: PlaywrightCrawlingContext) -> None:
        """Async handler for product page scraping"""
        page = context_obj.page
        url = context_obj.request.url

        logger.info(f"Scraping: {url}")

        # Wait for product list to load
        await page.wait_for_selector(
            manufacturer["selectors"]["product_list"], timeout=30000
        )

        # Extract products
        products = await page.query_selector_all(
            manufacturer["selectors"]["product_list"]
        )

        for product in products:
            try:
                # Extract product data
                title = await product.query_selector("h3, .product-title")
                title_text = await title.inner_text() if title else "Unknown"

                # Extract datasheet link
                datasheet = await product.query_selector(
                    manufacturer["selectors"]["datasheet"]
                )
                datasheet_url = (
                    await datasheet.get_attribute("href") if datasheet else None
                )

                # Extract image
                image = await product.query_selector(
                    manufacturer["selectors"]["images"]
                )
                image_url = await image.get_attribute("src") if image else None

                product_data = {
                    "manufacturer": manufacturer["name"],
                    "title": title_text.strip(),
                    "datasheet_url": datasheet_url,
                    "image_url": image_url,
                    "source_url": url,
                    "extracted_at": datetime.now().isoformat(),
                }

                extracted_products.append(product_data)
                logger.info(f"Extracted: {title_text}")

            except Exception as e:
                logger.error(f"Error extracting product: {e}")
                continue

    # Initialize crawler
    async def run_crawler():
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=100,
            max_concurrency=5,
            request_handler=scrape_products,
        )

        # Add starting URLs
        start_url = f"{manufacturer['website']}/products"
        await crawler.run([start_url])

    # Execute async crawler
    asyncio.run(run_crawler())

    logger.info(
        f"Extracted {len(extracted_products)} products from {manufacturer['name']}"
    )

    # Push to XCom for next task
    context["task_instance"].xcom_push(
        key="extracted_products", value=extracted_products
    )

    return {
        "manufacturer": manufacturer["name"],
        "total_products": len(extracted_products),
        "status": "success",
    }


def download_datasheets(**context) -> Dict[str, Any]:
    """
    Download PDF datasheets to MinIO (S3-compatible storage).
    Parallel downloads with retry logic and deduplication.
    """
    from concurrent.futures import ThreadPoolExecutor
    import requests
    from pathlib import Path
    import hashlib

    products = context["task_instance"].xcom_pull(key="extracted_products")

    logger.info(f"Downloading datasheets for {len(products)} products")

    # Initialize MinIO/S3 hook
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = Variable.get("minio_datasheets_bucket", "ysh-datasheets")

    downloaded_files = []

    def download_single_datasheet(product: Dict) -> Dict:
        """Download single datasheet with retry"""
        if not product.get("datasheet_url"):
            return {"status": "skipped", "product": product["title"]}

        try:
            # Download PDF
            response = requests.get(product["datasheet_url"], timeout=30)
            response.raise_for_status()

            # Generate unique filename
            url_hash = hashlib.md5(product["datasheet_url"].encode()).hexdigest()[:8]
            filename = f"{product['manufacturer']}/{url_hash}_{Path(product['datasheet_url']).name}"

            # Upload to MinIO
            s3_hook.load_bytes(
                bytes_data=response.content,
                key=filename,
                bucket_name=bucket_name,
                replace=True,
            )

            logger.info(f"Downloaded: {filename}")

            return {
                "status": "success",
                "product": product["title"],
                "filename": filename,
                "s3_url": f"s3://{bucket_name}/{filename}",
            }

        except Exception as e:
            logger.error(f"Error downloading {product['title']}: {e}")
            return {"status": "failed", "product": product["title"], "error": str(e)}

    # Parallel download with thread pool
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_single_datasheet, products))

    downloaded_files = [r for r in results if r["status"] == "success"]

    context["task_instance"].xcom_push(
        key="downloaded_datasheets", value=downloaded_files
    )

    return {
        "total_downloaded": len(downloaded_files),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "status": "success",
    }


def extract_datasheet_specs(**context) -> Dict[str, Any]:
    """
    Extract technical specifications from PDF datasheets using AI/OCR.
    Uses Ollama for local AI processing + pdfplumber for structured data.
    """
    import pdfplumber
    import polars as pl
    from ollama import Client

    datasheets = context["task_instance"].xcom_pull(key="downloaded_datasheets")
    s3_hook = S3Hook(aws_conn_id="minio_default")

    logger.info(f"Extracting specs from {len(datasheets)} datasheets")

    # Initialize Ollama client
    ollama_client = Client(host=Variable.get("ollama_host", "http://localhost:11434"))

    extracted_specs = []

    for datasheet in datasheets:
        try:
            # Download PDF from MinIO
            pdf_content = s3_hook.read_key(
                key=datasheet["filename"],
                bucket_name=Variable.get("minio_datasheets_bucket"),
            )

            # Extract text with pdfplumber
            with pdfplumber.open(pdf_content) as pdf:
                full_text = "\n".join(
                    [page.extract_text() for page in pdf.pages if page.extract_text()]
                )

            # Use Ollama to extract structured specs
            prompt = f"""
            Extract technical specifications from this solar equipment datasheet.
            
            Return JSON format with:
            - model: string
            - power_rating: number (Watts)
            - voltage: number (Volts)
            - current: number (Amps)
            - efficiency: number (percentage)
            - dimensions: string
            - weight: number (kg)
            - warranty_years: number
            - certifications: array of strings
            
            Datasheet text:
            {full_text[:3000]}
            """

            response = ollama_client.generate(
                model="llama3.2", prompt=prompt, format="json"
            )

            specs = json.loads(response["response"])
            specs["datasheet_s3_url"] = datasheet["s3_url"]
            specs["product_title"] = datasheet["product"]

            extracted_specs.append(specs)
            logger.info(f"Extracted specs for: {datasheet['product']}")

        except Exception as e:
            logger.error(f"Error extracting specs from {datasheet['product']}: {e}")
            continue

    # Convert to Polars for high-performance processing
    df_specs = pl.DataFrame(extracted_specs)

    # Save to XCom
    context["task_instance"].xcom_push(key="extracted_specs", value=df_specs.to_dicts())

    return {"total_extracted": len(extracted_specs), "status": "success"}


def download_product_images(**context) -> Dict[str, Any]:
    """
    Download and optimize product images for Medusa commerce platform.
    Parallel downloads + image optimization (WebP conversion, resizing).
    """
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image
    import requests
    from io import BytesIO
    import hashlib

    products = context["task_instance"].xcom_pull(key="extracted_products")
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = Variable.get("minio_images_bucket", "ysh-product-images")

    logger.info(f"Downloading images for {len(products)} products")

    def process_single_image(product: Dict) -> Dict:
        """Download and optimize single image"""
        if not product.get("image_url"):
            return {"status": "skipped", "product": product["title"]}

        try:
            # Download image
            response = requests.get(product["image_url"], timeout=30)
            response.raise_for_status()

            # Open with PIL
            img = Image.open(BytesIO(response.content))

            # Convert to RGB if needed
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Resize for web (max 1200px width)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save as WebP (better compression)
            webp_buffer = BytesIO()
            img.save(webp_buffer, format="WEBP", quality=85)
            webp_buffer.seek(0)

            # Generate filename
            url_hash = hashlib.md5(product["image_url"].encode()).hexdigest()[:8]
            filename = f"{product['manufacturer']}/{url_hash}.webp"

            # Upload to MinIO
            s3_hook.load_bytes(
                bytes_data=webp_buffer.read(),
                key=filename,
                bucket_name=bucket_name,
                replace=True,
            )

            # Also create thumbnail (300px)
            img_thumb = img.copy()
            img_thumb.thumbnail((300, 300), Image.Resampling.LANCZOS)
            thumb_buffer = BytesIO()
            img_thumb.save(thumb_buffer, format="WEBP", quality=80)
            thumb_buffer.seek(0)

            thumb_filename = f"{product['manufacturer']}/{url_hash}_thumb.webp"
            s3_hook.load_bytes(
                bytes_data=thumb_buffer.read(),
                key=thumb_filename,
                bucket_name=bucket_name,
                replace=True,
            )

            logger.info(f"Processed image: {filename}")

            return {
                "status": "success",
                "product": product["title"],
                "image_url": f"s3://{bucket_name}/{filename}",
                "thumbnail_url": f"s3://{bucket_name}/{thumb_filename}",
            }

        except Exception as e:
            logger.error(f"Error processing image for {product['title']}: {e}")
            return {"status": "failed", "product": product["title"], "error": str(e)}

    # Parallel processing
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_single_image, products))

    processed_images = [r for r in results if r["status"] == "success"]

    context["task_instance"].xcom_push(key="processed_images", value=processed_images)

    return {
        "total_processed": len(processed_images),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "status": "success",
    }


def normalize_to_medusa_schema(**context) -> Dict[str, Any]:
    """
    Normalize extracted data to Medusa commerce platform schema.
    Maps manufacturer data to Medusa Product, Variant, and Image models.
    """
    import polars as pl

    products = context["task_instance"].xcom_pull(key="extracted_products")
    specs = context["task_instance"].xcom_pull(key="extracted_specs")
    images = context["task_instance"].xcom_pull(key="processed_images")

    logger.info("Normalizing data to Medusa schema")

    # Convert to Polars for efficient joins
    df_products = pl.DataFrame(products)
    df_specs = pl.DataFrame(specs) if specs else pl.DataFrame()
    df_images = pl.DataFrame(images)

    # Join data
    df_merged = df_products.join(
        df_specs, left_on="title", right_on="product_title", how="left"
    ).join(df_images, left_on="title", right_on="product", how="left")

    # Map to Medusa schema
    medusa_products = []

    for row in df_merged.iter_rows(named=True):
        product = {
            # Core Medusa fields
            "title": row["title"],
            "subtitle": row.get("model", ""),
            "description": f"High-quality solar equipment from {row['manufacturer']}",
            "handle": row["title"].lower().replace(" ", "-"),
            "status": "published",
            "is_giftcard": False,
            "discountable": True,
            # Product type & collection
            "type": {"value": "solar-equipment"},
            "collection": {"handle": row["manufacturer"].lower().replace(" ", "-")},
            # Metadata (custom fields)
            "metadata": {
                "manufacturer": row["manufacturer"],
                "power_rating_w": row.get("power_rating"),
                "voltage_v": row.get("voltage"),
                "current_a": row.get("current"),
                "efficiency_pct": row.get("efficiency"),
                "dimensions": row.get("dimensions"),
                "weight_kg": row.get("weight"),
                "warranty_years": row.get("warranty_years"),
                "certifications": row.get("certifications", []),
                "datasheet_url": row.get("datasheet_s3_url"),
                "source_url": row.get("source_url"),
                "extracted_at": row.get("extracted_at"),
            },
            # Images
            "images": [
                {
                    "url": row.get("image_url"),
                    "metadata": {"thumbnail_url": row.get("thumbnail_url")},
                }
            ],
            # Variants
            "variants": [
                {
                    "title": "Standard",
                    "sku": f"{row['manufacturer'][:3].upper()}-{row.get('model', 'UNK')}".replace(
                        " ", "-"
                    ),
                    "manage_inventory": True,
                    "inventory_quantity": 0,
                    "allow_backorder": False,
                    "material": "solar-grade",
                    "weight": row.get("weight"),
                    "metadata": {"power_rating": row.get("power_rating")},
                }
            ],
        }

        medusa_products.append(product)

    # Save normalized data
    context["task_instance"].xcom_push(key="medusa_products", value=medusa_products)

    logger.info(f"Normalized {len(medusa_products)} products to Medusa schema")

    return {"total_normalized": len(medusa_products), "status": "success"}


def load_to_postgres(**context) -> Dict[str, Any]:
    """
    Load normalized data to PostgreSQL staging tables.
    Prepares data for Medusa import via custom module.
    """
    import json

    medusa_products = context["task_instance"].xcom_pull(key="medusa_products")

    logger.info(f"Loading {len(medusa_products)} products to PostgreSQL")

    # Get PostgreSQL hook
    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    # Insert into staging table
    insert_count = 0

    for product in medusa_products:
        try:
            cursor.execute(
                """
                INSERT INTO product_staging (
                    manufacturer,
                    title,
                    handle,
                    product_data,
                    created_at
                ) VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (handle) DO UPDATE SET
                    product_data = EXCLUDED.product_data,
                    updated_at = NOW()
                """,
                (
                    product["metadata"]["manufacturer"],
                    product["title"],
                    product["handle"],
                    json.dumps(product),
                ),
            )
            insert_count += 1

        except Exception as e:
            logger.error(f"Error inserting {product['title']}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"Loaded {insert_count} products to staging table")

    return {"total_loaded": insert_count, "status": "success"}


# ============================================================================
# DAG DEFINITION
# ============================================================================

with DAG(
    dag_id="manufacturer_data_extraction",
    default_args=default_args,
    description="High-performance extraction of manufacturer datasheets and images for YSH catalog",
    schedule_interval="0 2 * * 0",  # Weekly on Sundays at 2 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ysh", "data-extraction", "solar", "manufacturers"],
    doc_md=__doc__,
) as dag:

    # Task 1: Create staging table if not exists
    create_staging_table = PostgresOperator(
        task_id="create_staging_table",
        postgres_conn_id="postgres_default",
        sql="""
        CREATE TABLE IF NOT EXISTS product_staging (
            id SERIAL PRIMARY KEY,
            manufacturer VARCHAR(255) NOT NULL,
            title VARCHAR(500) NOT NULL,
            handle VARCHAR(500) UNIQUE NOT NULL,
            product_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            sync_status VARCHAR(50) DEFAULT 'pending'
        );
        
        CREATE INDEX IF NOT EXISTS idx_staging_manufacturer ON product_staging(manufacturer);
        CREATE INDEX IF NOT EXISTS idx_staging_sync_status ON product_staging(sync_status);
        """,
    )

    # Task 2: Extract catalog from manufacturer website
    extract_catalog = PythonOperator(
        task_id="extract_manufacturer_catalog",
        python_callable=extract_manufacturer_catalog,
        provide_context=True,
    )

    # Task 3: Download PDF datasheets in parallel
    download_pdfs = PythonOperator(
        task_id="download_datasheets",
        python_callable=download_datasheets,
        provide_context=True,
    )

    # Task 4: Extract specs from PDFs using AI
    extract_specs = PythonOperator(
        task_id="extract_datasheet_specifications",
        python_callable=extract_datasheet_specs,
        provide_context=True,
    )

    # Task 5: Download and optimize product images
    download_images = PythonOperator(
        task_id="download_product_images",
        python_callable=download_product_images,
        provide_context=True,
    )

    # Task 6: Normalize to Medusa commerce schema
    normalize_data = PythonOperator(
        task_id="normalize_to_medusa_schema",
        python_callable=normalize_to_medusa_schema,
        provide_context=True,
    )

    # Task 7: Load to PostgreSQL staging
    load_postgres = PythonOperator(
        task_id="load_to_postgresql",
        python_callable=load_to_postgres,
        provide_context=True,
    )

    # Define task dependencies
    create_staging_table >> extract_catalog
    extract_catalog >> [download_pdfs, download_images]
    download_pdfs >> extract_specs
    [extract_specs, download_images] >> normalize_data
    normalize_data >> load_postgres


# ============================================================================
# DYNAMIC DAG GENERATION - Create separate DAG for each manufacturer
# ============================================================================


def create_manufacturer_dag(manufacturer: Dict) -> DAG:
    """Factory function to create DAG for specific manufacturer"""
    dag_id = f"extract_{manufacturer['name'].lower().replace(' ', '_')}"

    return DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=f"Data extraction for {manufacturer['name']}",
        schedule_interval="0 3 * * 1",  # Weekly on Mondays at 3 AM
        start_date=datetime(2025, 1, 1),
        catchup=False,
        max_active_runs=1,
        tags=["ysh", "manufacturer", manufacturer["name"]],
        params={"manufacturer": manufacturer},
    )


# Generate individual DAGs for each manufacturer
for mfr in MANUFACTURERS:
    globals()[f"dag_{mfr['name'].lower().replace(' ', '_')}"] = create_manufacturer_dag(
        mfr
    )
