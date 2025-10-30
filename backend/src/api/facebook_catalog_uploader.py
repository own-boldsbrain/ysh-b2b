"""
Facebook Catalog Batch Uploader
Processa fila Redis e faz upload em lote para Facebook Catalog API
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

import redis
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.productcatalog import ProductCatalog
from facebook_business.adobjects.productitem import ProductItem
from facebook_business.exceptions import FacebookRequestError
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_CATALOG_ID = os.getenv("FACEBOOK_CATALOG_ID")
MOCK_MODE = os.getenv("MOCK_FACEBOOK_API", "false").lower() == "true"

BATCH_SIZE = int(os.getenv("FB_BATCH_SIZE", "100"))
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


class FacebookCatalogUploader:
    """Gerencia uploads em lote para Facebook Catalog"""
    
    def __init__(self):
        if not MOCK_MODE:
            FacebookAdsApi.init(
                app_id=FACEBOOK_APP_ID,
                app_secret=FACEBOOK_APP_SECRET,
                access_token=FACEBOOK_ACCESS_TOKEN
            )
            self.catalog = ProductCatalog(FACEBOOK_CATALOG_ID)
        
        self.redis_client = redis.from_url(REDIS_URL)
        self.db_conn = psycopg2.connect(DATABASE_URL)
    
    def fetch_products_for_manufacturer(self, manufacturer_id: int) -> List[Dict]:
        """Busca produtos processados no banco"""
        cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                p.id,
                p.model,
                p.specs_json,
                p.image_url,
                m.name as manufacturer_name,
                ep.sku,
                ep.category
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            LEFT JOIN enriched_products ep ON p.id = ep.product_id
            WHERE p.manufacturer_id = %s
              AND p.facebook_uploaded = false
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (manufacturer_id, BATCH_SIZE))
        products = cursor.fetchall()
        cursor.close()
        
        return [dict(p) for p in products]
    
    def format_product_for_facebook(self, product: Dict) -> Dict:
        """
        Formata produto para schema do Facebook Catalog
        Ref: https://developers.facebook.com/docs/marketing-api/catalog/
        """
        specs = json.loads(product.get('specs_json', '{}'))
        
        # Monta título descritivo
        title = f"{product['manufacturer_name']} {product['model']}"
        if product.get('category'):
            title = f"{product['category']} {title}"
        
        # Descrição técnica
        description_parts = [f"SKU: {product.get('sku', 'N/A')}"]
        for key, value in list(specs.items())[:5]:
            description_parts.append(f"{key}: {value}")
        description = " | ".join(description_parts)
        
        # URL do produto (ajustar para URL real da sua loja)
        product_url = f"https://yshsolar.com.br/produtos/{product.get('sku', product['id'])}"
        
        # Imagem (deve ser URL pública acessível)
        image_url = product.get('image_url') or "https://yshsolar.com.br/placeholder.jpg"
        
        return {
            "retailer_id": str(product['id']),  # ID único do produto
            "title": title[:150],  # Max 150 chars
            "description": description[:5000],  # Max 5000 chars
            "availability": "in stock",
            "condition": "new",
            "price": "0 BRL",  # Preço sob consulta
            "link": product_url,
            "image_link": image_url,
            "brand": product['manufacturer_name'],
            "google_product_category": "594",  # Solar Panels category
            "custom_label_0": product.get('category', 'Solar'),
            "custom_label_1": product.get('sku', '')[:100]
        }
    
    def upload_batch(self, products: List[Dict]) -> Dict:
        """
        Faz upload de um lote de produtos
        """
        if MOCK_MODE:
            logger.info(f"[MOCK] Would upload {len(products)} products")
            return {
                "success": len(products),
                "failed": 0,
                "mock": True
            }
        
        formatted_products = [
            self.format_product_for_facebook(p) for p in products
        ]
        
        try:
            # Batch request para o Facebook
            batch_request = []
            for prod in formatted_products:
                batch_request.append({
                    "method": "POST",
                    "relative_url": f"{FACEBOOK_CATALOG_ID}/products",
                    "body": prod
                })
            
            # Envia batch (max 50 por vez)
            success_count = 0
            failed_count = 0
            
            for i in range(0, len(batch_request), 50):
                batch_chunk = batch_request[i:i+50]
                
                try:
                    response = FacebookAdsApi.get_default_api().call(
                        'POST',
                        '',
                        params={'batch': json.dumps(batch_chunk)}
                    )
                    
                    # Processa respostas
                    for result in response:
                        if result.get('code') == 200:
                            success_count += 1
                        else:
                            failed_count += 1
                            logger.error(f"Failed item: {result}")
                    
                    time.sleep(1)  # Rate limiting
                
                except FacebookRequestError as e:
                    logger.error(f"Batch request failed: {e}")
                    failed_count += len(batch_chunk)
            
            return {
                "success": success_count,
                "failed": failed_count,
                "mock": False
            }
        
        except Exception as e:
            logger.error(f"Upload batch exception: {e}")
            return {
                "success": 0,
                "failed": len(products),
                "error": str(e)
            }
    
    def mark_as_uploaded(self, product_ids: List[int]):
        """Marca produtos como enviados ao Facebook"""
        cursor = self.db_conn.cursor()
        
        cursor.execute(
            """
            UPDATE products
            SET facebook_uploaded = true,
                facebook_uploaded_at = NOW()
            WHERE id = ANY(%s)
            """,
            (product_ids,)
        )
        
        self.db_conn.commit()
        cursor.close()
    
    def process_queue(self):
        """
        Loop principal: consome fila Redis e processa uploads
        """
        logger.info("Starting Facebook upload worker...")
        logger.info(f"Mock mode: {MOCK_MODE}")
        
        while True:
            try:
                # Pop job da fila (blocking com timeout de 30s)
                job_data = self.redis_client.brpop("facebook_upload_queue", timeout=30)
                
                if not job_data:
                    logger.debug("Queue empty, waiting...")
                    continue
                
                # Parse job
                _, job_json = job_data
                job = json.loads(job_json)
                
                manufacturer_id = job['manufacturer_id']
                manufacturer_name = job['manufacturer_name']
                
                logger.info(f"Processing upload for {manufacturer_name} (ID: {manufacturer_id})")
                
                # Busca produtos
                products = self.fetch_products_for_manufacturer(manufacturer_id)
                
                if not products:
                    logger.warning(f"No products found for manufacturer {manufacturer_id}")
                    continue
                
                logger.info(f"Found {len(products)} products to upload")
                
                # Upload em batch
                result = self.upload_batch(products)
                
                logger.info(f"Upload result: {result}")
                
                # Marca como enviados
                if result['success'] > 0:
                    product_ids = [p['id'] for p in products[:result['success']]]
                    self.mark_as_uploaded(product_ids)
                
                time.sleep(2)  # Rate limiting entre batches
            
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            
            except Exception as e:
                logger.error(f"Error in process_queue: {e}")
                time.sleep(5)
        
        self.db_conn.close()


def main():
    uploader = FacebookCatalogUploader()
    uploader.process_queue()


if __name__ == "__main__":
    main()
