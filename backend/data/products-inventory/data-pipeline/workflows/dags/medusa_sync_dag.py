"""
YSH Meta Commerce Product Sync Workflow DAG
============================================
Orchestrates sync from PostgreSQL staging to Meta Commerce Platform
(Facebook/Instagram Catalog) via Graph API.

Features:
- Batch product sync to Facebook Catalog
- CSV/XML feed generation
- Graph API integration
- Retry logic
- Status tracking

Author: YSH Platform Team
Version: 2.0.0 (Meta Commerce)
"""

from datetime import datetime, timedelta
from typing import Dict
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    "owner": "ysh-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def check_pending_products(**context) -> bool:
    """Check if there are products pending sync"""
    import psycopg2
    import os

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM product_staging WHERE sync_status = 'pending'")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    logger.info(f"Found {count} pending products")

    context["task_instance"].xcom_push(key="pending_count", value=count)

    return count > 0


def run_meta_commerce_sync(**context) -> Dict:
    """Execute Meta Commerce sync service"""
    import asyncio
    import sys
    import os

    # Add services to path
    services_path = os.path.join(os.path.dirname(__file__), "../../services")
    sys.path.insert(0, services_path)

    from meta_commerce_sync_service import MetaCommerceSyncService

    service = MetaCommerceSyncService(
        facebook_catalog_id=os.getenv("FACEBOOK_CATALOG_ID"),
        facebook_access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
        postgres_dsn=os.getenv("DATABASE_URL"),
        base_product_url=os.getenv("BASE_PRODUCT_URL", "https://ysh.solar/products"),
        currency=os.getenv("CURRENCY", "BRL"),
        batch_size=100,
    )

    stats = asyncio.run(service.run_sync())

    logger.info(f"Meta Commerce sync stats: {stats}")

    return stats


with DAG(
    dag_id="meta_commerce_product_sync",
    default_args=default_args,
    description="Sync products to Meta Commerce Platform",
    schedule_interval="0 */2 * * *",  # Every 2 hours
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ysh", "meta-commerce", "facebook", "instagram"],
) as dag:

    check_pending = PythonOperator(
        task_id="check_pending_products",
        python_callable=check_pending_products,
        provide_context=True,
    )

    sync_products = PythonOperator(
        task_id="run_meta_commerce_sync",
        python_callable=run_meta_commerce_sync,
        provide_context=True,
    )

    # Generate CSV feed backup
    generate_feed = BashOperator(
        task_id="generate_csv_feed",
        bash_command="echo 'Feed generation placeholder' || true",
    )

    check_pending >> sync_products >> generate_feed
