"""
YSH Solar B2B - Data Extraction & Database Upload Pipeline
Planejamento e execução de ETL para popular bancos de dados
"""

import os
import sys
import json
import csv
import psycopg2
from psycopg2.extras import execute_batch
import redis
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_extraction_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Configurações
BASE_PATH = Path(__file__).parent.parent
INVENTORY_PATH = BASE_PATH / "data" / "products-inventory"
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ysh_solar"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class DataExtractionPipeline:
    """
    Pipeline ETL para extrair dados do inventário e carregar nos bancos
    """

    def __init__(self):
        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.redis_client = redis.from_url(REDIS_URL)
        self.stats = {
            "manufacturers_inserted": 0,
            "products_inserted": 0,
            "images_inserted": 0,
            "errors": [],
        }

    # ==========================================
    # FASE 1: Extração de Fabricantes
    # ==========================================

    def extract_manufacturers(self) -> List[Dict]:
        """
        Extrai lista de fabricantes do manufacturers_unified_list.json
        """
        logger.info("FASE 1: Extraindo fabricantes...")

        file_path = INVENTORY_PATH / "manufacturers_unified_list.json"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        manufacturers = []
        for mfr in data["manufacturers"]:
            manufacturers.append(
                {
                    "name": mfr["name"],
                    "product_count": mfr["product_count"],
                    "priority": self._calculate_priority(mfr["product_count"]),
                    "active": True,
                    "base_url": self._get_manufacturer_url(mfr["name"]),
                }
            )

        logger.info(f"✓ Extraídos {len(manufacturers)} fabricantes")
        return manufacturers

    def _calculate_priority(self, product_count: int) -> int:
        """Calcula prioridade baseado no número de produtos"""
        if product_count >= 1000:
            return 100
        elif product_count >= 500:
            return 90
        elif product_count >= 100:
            return 80
        elif product_count >= 50:
            return 70
        else:
            return 60

    def _get_manufacturer_url(self, name: str) -> str:
        """Retorna URL oficial do fabricante (mapeamento manual)"""
        url_map = {
            "Deye": "https://www.deyeinverter.com/",
            "EPever": "https://www.epever.com/",
            "DAH Solar": "https://www.dahsolar.com/",
            "Ztroon": "https://www.ztroon.com/",
            "Znshine": "https://www.znshinesolar.com/",
            "Sunova": "https://www.sunovasolar.com/",
            "Moura": "https://www.moura.com.br/",
            "LONGi": "https://www.longi.com/en/",
            "OSDA Solar": "https://www.osda-solar.com/",
            "UCB": "https://www.ucb.ind.br/",
            "Freedom": "https://www.freedomdf.com.br/",
            "Unipower": "https://www.unipower.ind.br/",
            "GoodWe": "https://www.goodwe.com/",
            "ReneSola": "https://www.renesola.com/",
            "BYD": "https://www.bydbatterybox.com/",
            "Growatt": "https://www.growatt.com/",
            "Risen Energy": "https://www.risenenergy.com/",
            "Sungrow": "https://www.sungrowpower.com/",
            "Enphase": "https://enphase.com/",
            "Huawei": "https://solar.huawei.com/",
            "Trina Solar": "https://www.trinasolar.com/",
            "Jinko Solar": "https://www.jinkosolar.com/",
            "Canadian Solar": "https://www.canadiansolar.com/",
            "JA Solar": "https://www.jasolar.com/",
        }
        return url_map.get(
            name, f"https://www.google.com/search?q={name.replace(' ', '+')}+solar"
        )

    def load_manufacturers(self, manufacturers: List[Dict]) -> int:
        """
        Carrega fabricantes no PostgreSQL
        """
        logger.info("Carregando fabricantes no banco...")

        cursor = self.db_conn.cursor()

        insert_query = """
            INSERT INTO manufacturers (name, base_url, priority, active)
            VALUES (%(name)s, %(base_url)s, %(priority)s, %(active)s)
            ON CONFLICT (name) DO UPDATE SET
                base_url = EXCLUDED.base_url,
                priority = EXCLUDED.priority,
                active = EXCLUDED.active,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """

        inserted = 0
        for mfr in manufacturers:
            try:
                cursor.execute(insert_query, mfr)
                inserted += 1
            except Exception as e:
                logger.error(f"Erro ao inserir {mfr['name']}: {e}")
                self.stats["errors"].append(f"Manufacturer {mfr['name']}: {e}")

        self.db_conn.commit()
        cursor.close()

        self.stats["manufacturers_inserted"] = inserted
        logger.info(f"✓ {inserted} fabricantes carregados")
        return inserted

    # ==========================================
    # FASE 2: Extração de Produtos
    # ==========================================

    def extract_products(self) -> List[Dict]:
        """
        Extrai produtos do unified_products.json
        """
        logger.info("FASE 2: Extraindo produtos...")

        file_path = INVENTORY_PATH / "unified_products.json"

        with open(file_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        logger.info(f"✓ Extraídos {len(products)} produtos")
        return products

    def transform_product(
        self, product: Dict, manufacturer_map: Dict[str, int]
    ) -> Optional[Dict]:
        """
        Transforma produto para schema do banco
        """
        try:
            # Determina fabricante principal
            main_manufacturer = None

            # Tenta extrair de painéis
            if product.get("components", {}).get("panels"):
                panel = product["components"]["panels"][0]
                main_manufacturer = panel.get("manufacturer")

            # Tenta extrair de inversores
            if not main_manufacturer and product.get("components", {}).get("inverters"):
                inverter = product["components"]["inverters"][0]
                main_manufacturer = inverter.get("manufacturer")

            # Fallback para distribuidor
            if not main_manufacturer:
                main_manufacturer = product.get("distributor")

            if not main_manufacturer or main_manufacturer not in manufacturer_map:
                return None

            # Extrai especificações técnicas
            specs = {
                "power_kwp": product.get("power", {}).get("kwp"),
                "power_watts": product.get("power", {}).get("watts"),
                "category": product.get("category"),
                "type": product.get("type"),
                "components": product.get("components"),
                "totals": product.get("totals"),
                "pricing": product.get("pricing"),
                "tags": product.get("tags", []),
            }

            # Extrai imagem principal
            image_url = product.get("media", {}).get("image_url", "")
            if not image_url and product.get("components", {}).get("panels"):
                image_url = product["components"]["panels"][0].get("image", "")

            return {
                "manufacturer_id": manufacturer_map[main_manufacturer],
                "model": product.get("name", product.get("id", "Unknown")),
                "title": product.get("name"),
                "specs_json": json.dumps(specs),
                "image_url": image_url if image_url else None,
            }

        except Exception as e:
            logger.error(f"Erro ao transformar produto {product.get('id')}: {e}")
            return None

    def load_products(self, products: List[Dict]) -> int:
        """
        Carrega produtos no PostgreSQL em batch
        """
        logger.info("Transformando e carregando produtos...")

        # Busca mapeamento de fabricantes
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, name FROM manufacturers")
        manufacturer_map = {name: id for id, name in cursor.fetchall()}

        # Transforma produtos
        transformed = []
        for product in products:
            t_product = self.transform_product(product, manufacturer_map)
            if t_product:
                transformed.append(t_product)

        logger.info(
            f"✓ {len(transformed)} produtos transformados de {len(products)} totais"
        )

        # Insere em batch
        insert_query = """
            INSERT INTO products (manufacturer_id, model, title, specs_json, image_url)
            VALUES (%(manufacturer_id)s, %(model)s, %(title)s, %(specs_json)s, %(image_url)s)
            ON CONFLICT (manufacturer_id, model) DO UPDATE SET
                title = EXCLUDED.title,
                specs_json = EXCLUDED.specs_json,
                image_url = EXCLUDED.image_url,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """

        inserted = 0
        batch_size = 100

        for i in range(0, len(transformed), batch_size):
            batch = transformed[i : i + batch_size]
            try:
                execute_batch(cursor, insert_query, batch, page_size=batch_size)
                inserted += len(batch)
                logger.info(
                    f"  Batch {i//batch_size + 1}: {inserted}/{len(transformed)} produtos"
                )
            except Exception as e:
                logger.error(f"Erro no batch {i//batch_size + 1}: {e}")
                self.stats["errors"].append(f"Product batch {i}-{i+batch_size}: {e}")

        self.db_conn.commit()
        cursor.close()

        self.stats["products_inserted"] = inserted
        logger.info(f"✓ {inserted} produtos carregados")
        return inserted

    # ==========================================
    # FASE 3: Extração de Imagens
    # ==========================================

    def extract_and_load_images(self) -> int:
        """
        Extrai URLs de imagens dos produtos e registra na tabela product_images
        """
        logger.info("FASE 3: Extraindo e carregando imagens...")

        cursor = self.db_conn.cursor()

        # Busca produtos com imagens
        cursor.execute(
            """
            SELECT id, model, image_url, specs_json
            FROM products
            WHERE image_url IS NOT NULL AND image_url != ''
        """
        )

        products_with_images = cursor.fetchall()
        logger.info(f"Encontrados {len(products_with_images)} produtos com imagens")

        insert_query = """
            INSERT INTO product_images (product_id, url, quality_score, width, height)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """

        inserted = 0
        for product_id, model, image_url, specs_json in products_with_images:
            try:
                # Score inicial baseado em URL
                quality_score = 5  # Default
                if "prod-platform-api" in image_url:
                    quality_score = 7  # Imagens oficiais

                # Dimensões estimadas (ajustar depois com download real)
                width = 800
                height = 800

                cursor.execute(
                    insert_query, (product_id, image_url, quality_score, width, height)
                )
                inserted += 1

            except Exception as e:
                logger.error(f"Erro ao inserir imagem do produto {model}: {e}")

        self.db_conn.commit()
        cursor.close()

        self.stats["images_inserted"] = inserted
        logger.info(f"✓ {inserted} imagens registradas")
        return inserted

    # ==========================================
    # FASE 4: Cache Redis
    # ==========================================

    def populate_redis_cache(self):
        """
        Popula Redis com dados frequentes para consulta rápida
        """
        logger.info("FASE 4: Populando cache Redis...")

        cursor = self.db_conn.cursor()

        # Cache 1: Lista de fabricantes ativos
        cursor.execute(
            """
            SELECT name, base_url, priority
            FROM manufacturers
            WHERE active = true
            ORDER BY priority DESC
        """
        )

        manufacturers = cursor.fetchall()
        for name, url, priority in manufacturers:
            key = f"manufacturer:{name.lower().replace(' ', '_')}"
            self.redis_client.hset(
                key, mapping={"name": name, "url": url, "priority": priority}
            )
            self.redis_client.expire(key, 86400)  # 24 horas

        logger.info(f"✓ {len(manufacturers)} fabricantes em cache")

        # Cache 2: Top produtos por fabricante
        cursor.execute(
            """
            SELECT m.name, COUNT(p.id) as count
            FROM manufacturers m
            JOIN products p ON m.id = p.manufacturer_id
            GROUP BY m.id, m.name
            ORDER BY count DESC
        """
        )

        for mfr_name, count in cursor.fetchall():
            key = f"stats:products:{mfr_name.lower().replace(' ', '_')}"
            self.redis_client.set(key, count, ex=86400)

        cursor.close()
        logger.info("✓ Estatísticas em cache")

    # ==========================================
    # FASE 5: Validação e Relatório
    # ==========================================

    def validate_and_report(self):
        """
        Valida dados carregados e gera relatório
        """
        logger.info("FASE 5: Validando dados...")

        cursor = self.db_conn.cursor()

        # Validações
        validations = {
            "manufacturers": "SELECT COUNT(*) FROM manufacturers",
            "active_manufacturers": "SELECT COUNT(*) FROM manufacturers WHERE active = true",
            "products": "SELECT COUNT(*) FROM products",
            "products_with_images": "SELECT COUNT(*) FROM products WHERE image_url IS NOT NULL",
            "product_images": "SELECT COUNT(*) FROM product_images",
            "avg_products_per_mfr": "SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM products GROUP BY manufacturer_id) sub",
        }

        results = {}
        for key, query in validations.items():
            cursor.execute(query)
            results[key] = cursor.fetchone()[0]

        cursor.close()

        # Gera relatório
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          YSH SOLAR B2B - DATA EXTRACTION REPORT             ║
╚══════════════════════════════════════════════════════════════╝

📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 ESTATÍSTICAS DE EXTRAÇÃO:

  Fabricantes:
    ✓ Total carregados: {self.stats['manufacturers_inserted']}
    ✓ Ativos no banco: {results['active_manufacturers']}
    ✓ Total no banco: {results['manufacturers']}

  Produtos:
    ✓ Total carregados: {self.stats['products_inserted']}
    ✓ Total no banco: {results['products']}
    ✓ Com imagens: {results['products_with_images']}
    ✓ Média por fabricante: {results['avg_products_per_mfr']:.1f}

  Imagens:
    ✓ Total registradas: {self.stats['images_inserted']}
    ✓ Total no banco: {results['product_images']}

❌ ERROS ENCONTRADOS: {len(self.stats['errors'])}
"""

        if self.stats["errors"]:
            report += "\n  Detalhes dos erros:\n"
            for i, error in enumerate(self.stats["errors"][:10], 1):
                report += f"    {i}. {error}\n"
            if len(self.stats["errors"]) > 10:
                report += f"    ... e mais {len(self.stats['errors']) - 10} erros\n"

        report += """
✅ STATUS: Pipeline executado com sucesso!

📝 PRÓXIMOS PASSOS:
  1. Revisar erros (se houver) no log: data_extraction_pipeline.log
  2. Executar scraper para baixar imagens: python src/scrapers/ai_guided_scraper.py
  3. Iniciar Dagster para schedules: docker-compose up -d dagster-webserver
  4. Monitorar em: http://localhost:3000

╚══════════════════════════════════════════════════════════════╝
"""

        print(report)
        logger.info("Pipeline concluído!")

        # Salva relatório
        report_path = BASE_PATH / "data" / "extraction_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return results

    # ==========================================
    # Método Principal
    # ==========================================

    def run(self):
        """
        Executa pipeline completo
        """
        logger.info("=" * 70)
        logger.info("INICIANDO DATA EXTRACTION PIPELINE")
        logger.info("=" * 70)

        try:
            # Fase 1: Fabricantes
            manufacturers = self.extract_manufacturers()
            self.load_manufacturers(manufacturers)

            # Fase 2: Produtos
            products = self.extract_products()
            self.load_products(products)

            # Fase 3: Imagens
            self.extract_and_load_images()

            # Fase 4: Cache
            self.populate_redis_cache()

            # Fase 5: Validação
            self.validate_and_report()

        except Exception as e:
            logger.error(f"ERRO CRÍTICO no pipeline: {e}")
            raise

        finally:
            self.db_conn.close()
            logger.info("Pipeline finalizado")


def main():
    """
    Ponto de entrada
    """
    pipeline = DataExtractionPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
