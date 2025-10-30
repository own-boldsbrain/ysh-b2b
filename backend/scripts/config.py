"""
Configurações Globais para os Scripts de Scraping.

Este arquivo centraliza as configurações, como chaves de API,
listas de modelos e parâmetros de execução.
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Chaves de API ---
# As chaves são lidas das variáveis de ambiente para segurança.
# Crie um arquivo .env na raiz do projeto e adicione as chaves lá.
GEMINI_API_KEYS = [
    key for key in [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")] if key
]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Modelos Docker ---
# Lista de nomes dos containers dos modelos locais que podem ser usados como fallback.
DOCKER_MODELS = [
    "ai/smollm2:latest",
    "ai/gemma3-qat:latest",
    "ai/gpt-oss:latest",
    "ai/qwen3-coder:latest",
]

# --- Configurações de Scraping ---
# User-Agent para simular um navegador real.
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Limites e comportamento de requisições para não sobrecarregar os servidores.
REQUEST_TIMEOUT = 15  # segundos
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5  # Fator de espera entre tentativas (ex: 0.5s, 1s, 2s)
REQUESTS_PER_SECOND_PER_DOMAIN = 3

# --- Configurações de Processamento de Imagem ---
IMAGE_PRIMARY_SIZE = (1024, 1024)
IMAGE_SECONDARY_SIZE = (600, 600)
IMAGE_QUALITY = 90  # Qualidade do JPEG (0-100)
IMAGE_OUTPUT_FORMAT = "JPEG"
CANVAS_COLOR = (255, 255, 255)  # Fundo branco para letterboxing

# --- Caminhos de Saída ---
OUTPUT_DIR = "output"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
FEED_FILE = os.path.join(REPORTS_DIR, "meta_commerce_feed.json")
QA_REPORT_FILE = os.path.join(REPORTS_DIR, "qa_report.csv")
AUDIT_LOG_FILE = os.path.join(REPORTS_DIR, "audit_log.csv")

# --- Inventário ---
# Caminho para o arquivo de inventário que contém os SKUs a serem processados.
INVENTORY_FILE = "data/inventory/product_skus.csv"

# --- Validação ---
# Valide se as chaves de API essenciais foram carregadas.
if not GEMINI_API_KEYS and not OPENAI_API_KEY:
    print(
        "⚠️  Atenção: Nenhuma chave de API para Gemini ou OpenAI foi encontrada nas variáveis de ambiente."
    )
    print("   O sistema dependerá exclusivamente dos modelos Docker (se disponíveis).")

if not GEMINI_API_KEYS:
    print("⚠️  Chaves da API Gemini não configuradas.")

if not OPENAI_API_KEY:
    print("⚠️  Chave da API OpenAI não configurada.")
