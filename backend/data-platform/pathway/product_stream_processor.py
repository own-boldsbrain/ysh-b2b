"""
Pathway Real-Time Product Stream Processor
Processa novos produtos e enriquece com dados de SKU
"""
import os
import pathway as pw
from pathway.stdlib.ml.classifiers import KNeighborsClassifier
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ysh_solar")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def normalize_sku(model_name: str, manufacturer: str) -> str:
    """
    Normaliza nome de modelo para SKU padrão YSH
    Exemplo: "JKM550M-72HL4-V" -> "YSH-PAN-JKS-JKM550M72HL4V"
    """
    # Remove caracteres especiais
    clean_model = ''.join(c for c in model_name if c.isalnum())
    
    # Prefixo por fabricante (primeiras 3 letras)
    mfr_prefix = manufacturer[:3].upper()
    
    # Categoria (será classificada depois)
    category_map = {
        "inversor": "INV",
        "painel": "PAN",
        "bateria": "BAT",
        "estrutura": "EST",
        "cabo": "CAB",
        "kit": "KIT"
    }
    
    # Detecta categoria por palavras-chave
    category = "GEN"  # Genérico
    for keyword, code in category_map.items():
        if keyword in model_name.lower():
            category = code
            break
    
    return f"YSH-{category}-{mfr_prefix}-{clean_model}"


def classify_category(specs: dict) -> str:
    """
    Classifica produto em categoria baseado em specs técnicas
    """
    specs_text = json.dumps(specs).lower()
    
    if any(kw in specs_text for kw in ["potência pico", "wp", "células", "módulo"]):
        return "Painel Solar"
    elif any(kw in specs_text for kw in ["inversor", "mppt", "grid-tie", "off-grid"]):
        return "Inversor"
    elif any(kw in specs_text for kw in ["bateria", "ah", "ciclos", "lithium"]):
        return "Bateria"
    elif any(kw in specs_text for kw in ["estrutura", "fixação", "trilho"]):
        return "Estrutura"
    elif any(kw in specs_text for kw in ["cabo", "fio", "mm²"]):
        return "Cabo"
    else:
        return "Outros"


# Define schema do stream de entrada
class ProductInput(pw.Schema):
    manufacturer_id: int
    manufacturer_name: str
    model: str
    specs_json: str
    image_url: str | None
    scraped_at: str


# Pipeline Pathway
def run_processor():
    """
    Executa processador em tempo real
    """
    logger.info("Starting Pathway processor...")
    
    # Input: Conecta ao PostgreSQL (CDC - Change Data Capture)
    products_stream = pw.io.postgres.read(
        host="postgres",
        port=5432,
        dbname="ysh_solar",
        user="postgres",
        password="postgres",
        table_name="products",
        schema=ProductInput
    )
    
    # Transformação 1: Normaliza SKU
    enriched = products_stream.select(
        pw.this.manufacturer_id,
        pw.this.manufacturer_name,
        pw.this.model,
        sku=pw.apply(normalize_sku, pw.this.model, pw.this.manufacturer_name),
        specs=pw.apply(lambda x: json.loads(x), pw.this.specs_json),
        pw.this.image_url,
        pw.this.scraped_at
    )
    
    # Transformação 2: Classifica categoria
    categorized = enriched.select(
        pw.this.manufacturer_id,
        pw.this.manufacturer_name,
        pw.this.model,
        pw.this.sku,
        category=pw.apply(classify_category, pw.this.specs),
        pw.this.specs,
        pw.this.image_url,
        pw.this.scraped_at
    )
    
    # Output 1: Escreve de volta no PostgreSQL (tabela enriched_products)
    pw.io.postgres.write(
        categorized,
        host="postgres",
        port=5432,
        dbname="ysh_solar",
        user="postgres",
        password="postgres",
        table_name="enriched_products"
    )
    
    # Output 2: Publica no Redis para consumo downstream
    pw.io.redis.write(
        categorized,
        rdx=pw.io.redpanda.rdx_connector(
            host="redis",
            port=6379,
            db=0
        ),
        topic="enriched_products"
    )
    
    # Output 3: Log de monitoramento
    pw.io.jsonlines.write(categorized, "/output/pathway_processed.jsonl")
    
    logger.info("Pathway pipeline configured. Starting computation...")
    
    # Inicia computação (blocking)
    pw.run(monitoring_level=pw.MonitoringLevel.AUTO)


if __name__ == "__main__":
    run_processor()
