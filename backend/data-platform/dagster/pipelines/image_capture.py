"""
Dagster Pipeline: Captura Automática de Imagens de Produtos Solares
Orquestra scraping diário de fabricantes brasileiros e internacionais
"""

import os
from datetime import datetime
from typing import List, Dict, Any

from dagster import (
    job,
    op,
    In,
    Out,
    DynamicOut,
    DynamicOutput,
    graph,
    schedule,
    resource,
    ConfigurableResource,
    OpExecutionContext,
)
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json


# ============================================
# Resources
# ============================================


class DatabaseResource(ConfigurableResource):
    """PostgreSQL connection resource"""

    connection_string: str

    def get_connection(self):
        return psycopg2.connect(self.connection_string)


class RedisResource(ConfigurableResource):
    """Redis connection resource"""

    host: str = "redis"
    port: int = 6379
    db: int = 0

    def get_client(self):
        return redis.Redis(host=self.host, port=self.port, db=self.db)


# ============================================
# Ops (Operações)
# ============================================


@op(
    out=DynamicOut(Dict[str, Any]),
    description="Busca lista de fabricantes para scraping",
)
def fetch_manufacturer_list(context: OpExecutionContext, database: DatabaseResource):
    """
    Busca todos os fabricantes ativos do banco de dados
    Retorna um DynamicOutput para cada fabricante
    """
    conn = database.get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query para buscar fabricantes ativos
        query = """
            SELECT id, name, base_url, last_scraped, priority
            FROM manufacturers
            WHERE active = true
            ORDER BY priority DESC, last_scraped ASC NULLS FIRST
            LIMIT 50
        """
        cursor.execute(query)
        manufacturers = cursor.fetchall()

        context.log.info(f"Encontrados {len(manufacturers)} fabricantes para scraping")

        # Yield dynamic output para cada fabricante
        for mfr in manufacturers:
            yield DynamicOutput(value=dict(mfr), mapping_key=f"mfr_{mfr['id']}")

    finally:
        cursor.close()
        conn.close()


@op(
    ins={"manufacturer": In(Dict[str, Any])},
    out=Out(Dict[str, Any]),
    description="Executa scraping de um fabricante específico",
)
def scrape_manufacturer(
    context: OpExecutionContext, manufacturer: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Chama o scraper AI-guided para coletar imagens de produtos
    """
    import subprocess

    mfr_name = manufacturer["name"]
    mfr_url = manufacturer["base_url"]

    context.log.info(f"Iniciando scraping de {mfr_name} ({mfr_url})")

    # Chama o scraper Python com contexto do mega-prompt
    scraper_script = "/app/scrapers/ai_guided_scraper.py"

    try:
        result = subprocess.run(
            [
                "python",
                scraper_script,
                "--manufacturer",
                mfr_name,
                "--url",
                mfr_url,
                "--output-dir",
                f"/app/output/images/{mfr_name.lower().replace(' ', '_')}",
                "--max-products",
                "100",
            ],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutos max por fabricante
        )

        if result.returncode == 0:
            # Parse output JSON
            output_data = json.loads(result.stdout)
            context.log.info(
                f"Scraping concluído: {output_data.get('products_found', 0)} produtos"
            )

            return {
                "manufacturer_id": manufacturer["id"],
                "manufacturer_name": mfr_name,
                "status": "success",
                "products_found": output_data.get("products_found", 0),
                "images_downloaded": output_data.get("images_downloaded", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            context.log.error(f"Erro no scraping: {result.stderr}")
            return {
                "manufacturer_id": manufacturer["id"],
                "manufacturer_name": mfr_name,
                "status": "error",
                "error_message": result.stderr[:500],
                "timestamp": datetime.utcnow().isoformat(),
            }

    except subprocess.TimeoutExpired:
        context.log.error(f"Timeout no scraping de {mfr_name}")
        return {
            "manufacturer_id": manufacturer["id"],
            "manufacturer_name": mfr_name,
            "status": "timeout",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        context.log.error(f"Exceção no scraping: {str(e)}")
        return {
            "manufacturer_id": manufacturer["id"],
            "manufacturer_name": mfr_name,
            "status": "exception",
            "error_message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@op(
    ins={"scrape_result": In(Dict[str, Any])},
    out=Out(Dict[str, Any]),
    description="Processa e otimiza imagens baixadas",
)
def process_images(
    context: OpExecutionContext, scrape_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Aplica otimizações nas imagens:
    - Redimensiona para múltiplos tamanhos
    - Converte para WebP
    - Gera thumbnails
    - Calcula hashes para deduplicação
    """
    if scrape_result["status"] != "success":
        context.log.warning(
            f"Pulando processamento para {scrape_result['manufacturer_name']} (status: {scrape_result['status']})"
        )
        return scrape_result

    from PIL import Image
    import imagehash
    import os
    from pathlib import Path

    mfr_name = scrape_result["manufacturer_name"]
    images_dir = Path(f"/app/output/images/{mfr_name.lower().replace(' ', '_')}")

    if not images_dir.exists():
        context.log.warning(f"Diretório de imagens não encontrado: {images_dir}")
        return scrape_result

    processed_count = 0
    error_count = 0

    for img_path in images_dir.glob("*.jpg"):
        try:
            # Abre imagem original
            img = Image.open(img_path)

            # Calcula hash para deduplicação
            img_hash = str(imagehash.average_hash(img))

            # Gera versões otimizadas
            sizes = {
                "thumbnail": (300, 300),
                "medium": (800, 800),
                "large": (1600, 1600),
            }

            for size_name, (width, height) in sizes.items():
                img_resized = img.copy()
                img_resized.thumbnail((width, height), Image.Resampling.LANCZOS)

                # Salva como WebP
                webp_path = img_path.parent / f"{img_path.stem}_{size_name}.webp"
                img_resized.save(webp_path, "WEBP", quality=85, method=6)

            processed_count += 1

        except Exception as e:
            context.log.error(f"Erro ao processar {img_path.name}: {str(e)}")
            error_count += 1

    context.log.info(f"Processadas {processed_count} imagens, {error_count} erros")

    return {
        **scrape_result,
        "images_processed": processed_count,
        "processing_errors": error_count,
    }


@op(
    ins={"process_result": In(Dict[str, Any])},
    out=Out(Dict[str, Any]),
    description="Envia produtos para fila do Facebook Catalog",
)
def queue_facebook_upload(
    context: OpExecutionContext,
    process_result: Dict[str, Any],
    redis_res: RedisResource,
) -> Dict[str, Any]:
    """
    Adiciona produtos processados na fila Redis para upload no Facebook
    """
    if process_result["status"] != "success":
        return process_result

    redis_client = redis_res.get_client()

    # Adiciona job na fila
    job_data = {
        "manufacturer_id": process_result["manufacturer_id"],
        "manufacturer_name": process_result["manufacturer_name"],
        "products_count": process_result.get("products_found", 0),
        "timestamp": datetime.utcnow().isoformat(),
    }

    redis_client.lpush("facebook_upload_queue", json.dumps(job_data))
    context.log.info(
        f"Adicionado job de upload para {process_result['manufacturer_name']}"
    )

    return {**process_result, "facebook_queued": True}


@op(
    ins={"results": In(List[Dict[str, Any]])},
    description="Consolida resultados e atualiza banco de dados",
)
def update_scraping_log(
    context: OpExecutionContext,
    results: List[Dict[str, Any]],
    database: DatabaseResource,
):
    """
    Registra resultados do scraping no banco de dados
    """
    conn = database.get_connection()
    cursor = conn.cursor()

    try:
        for result in results:
            # Atualiza timestamp de last_scraped
            cursor.execute(
                """
                UPDATE manufacturers
                SET last_scraped = NOW(),
                    last_status = %s
                WHERE id = %s
                """,
                (result["status"], result["manufacturer_id"]),
            )

            # Insere log de scraping
            cursor.execute(
                """
                INSERT INTO scraping_logs (
                    manufacturer_id, 
                    status, 
                    products_found, 
                    images_downloaded,
                    error_message,
                    timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    result["manufacturer_id"],
                    result["status"],
                    result.get("products_found", 0),
                    result.get("images_downloaded", 0),
                    result.get("error_message"),
                    result["timestamp"],
                ),
            )

        conn.commit()
        context.log.info(f"Atualizados logs para {len(results)} fabricantes")

    finally:
        cursor.close()
        conn.close()


# ============================================
# Jobs (Pipelines)
# ============================================


@job(
    description="Pipeline diário de scraping de fabricantes",
    resource_defs={
        "database": DatabaseResource(connection_string=os.getenv("DATABASE_URL", "")),
        "redis_res": RedisResource(),
    },
)
def daily_manufacturer_scrape():
    """
    Job principal executado diariamente às 2AM UTC-3
    """
    # 1. Busca fabricantes (retorna dynamic outputs)
    manufacturers = fetch_manufacturer_list()

    # 2. Para cada fabricante, executa scraping, processamento e queue
    results = manufacturers.map(
        lambda mfr: queue_facebook_upload(process_images(scrape_manufacturer(mfr)))
    )

    # 3. Coleta todos os resultados e atualiza logs
    update_scraping_log(results.collect())


@job(
    description="Atualização semanal do catálogo completo",
    resource_defs={
        "database": DatabaseResource(connection_string=os.getenv("DATABASE_URL", "")),
        "redis_res": RedisResource(),
    },
)
def weekly_catalog_update():
    """
    Re-scrape completo de todos os fabricantes (incluindo inativos)
    Executado aos domingos às 3AM
    """
    # Implementação similar ao daily_manufacturer_scrape
    # mas inclui fabricantes inativos
    pass


# ============================================
# Schedules
# ============================================


@schedule(
    cron_schedule="0 2 * * *",  # 2AM todos os dias
    job=daily_manufacturer_scrape,
    execution_timezone="America/Sao_Paulo",
)
def daily_scrape_schedule(context):
    """Agenda diária de scraping"""
    return {}


@schedule(
    cron_schedule="0 3 * * 0",  # 3AM aos domingos
    job=weekly_catalog_update,
    execution_timezone="America/Sao_Paulo",
)
def weekly_update_schedule(context):
    """Agenda semanal de atualização completa"""
    return {}
