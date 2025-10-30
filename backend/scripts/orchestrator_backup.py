"""
Orquestrador Principal do Plano "Comandante A"

Este script gerencia o fluxo completo de captura de imagens:
1. Lê os SKUs do inventário.
2. Organiza a execução em ondas, conforme o plano.
3. Para cada SKU, invoca os módulos de scraping, processamento e QA.
4. Gera os relatórios finais e o feed para o Meta Commerce.
"""

import os
import pandas as pd
import requests
from tqdm import tqdm

from config import (
    INVENTORY_FILE,
    OUTPUT_DIR,
    IMAGE_DIR,
    REPORTS_DIR,
    FEED_FILE,
    QA_REPORT_FILE,
    AUDIT_LOG_FILE,
)
from sku_parser import parse_sku
from image_scraper import ImageScraper
from image_processor import process_image
from quality_assurance import qa_image
from knowledge_base_builder import KnowledgeBaseBuilder
from rag_finder import RAGFinder
from semantic_scraper import SemanticScraper


def setup_directories():
    """Cria os diretórios de saída se não existirem."""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    print("✅ Diretórios de saída verificados/criados.")


def load_inventory():
    """Carrega a lista de SKUs do arquivo de inventário."""
    if not os.path.exists(INVENTORY_FILE):
        print(f"❌ Erro: Arquivo de inventário não encontrado em '{INVENTORY_FILE}'")
        return []

    # Supondo um arquivo CSV com uma coluna 'sku'
    df = pd.read_csv(INVENTORY_FILE)
    print(f"📦 Inventário carregado com {len(df)} SKUs.")
    return df["sku"].tolist()


def define_waves(sku_list):
    """Divide a lista de SKUs nas ondas de execução definidas no plano."""
    # Lógica de priorização baseada no fabricante (extraído do SKU)
    # Exemplo simples:
    wave1_mfr = [
        "Growatt",
        "Deye",
        "Fronius",
        "GoodWe",
        "Solis",
        "Canadian",
        "Jinko",
        "Trina",
        "JA",
        "LONGi",
    ]
    wave2_mfr = [
        "SAJ",
        "Huawei",
        "SMA",
        "ABB",
        "Sungrow",
        "Risen",
        "Suntech",
        "Jinergy",
    ]

    waves = {"wave1": [], "wave2": [], "wave3": []}

    for sku in sku_list:
        parsed_info = parse_sku(sku)
        mfr = parsed_info.get("manufacturer", "").replace("-", " ").title()

        if any(w in mfr for w in wave1_mfr):
            waves["wave1"].append(sku)
        elif any(w in mfr for w in wave2_mfr):
            waves["wave2"].append(sku)
        else:
            waves["wave3"].append(sku)

    print(
        f"🌊 Ondas de execução definidas: {len(waves['wave1'])} na Onda 1, {len(waves['wave2'])} na Onda 2, {len(waves['wave3'])} na Onda 3."
    )
    return waves


def ensure_knowledge_base(manufacturer: str, base_url: str) -> str:
    """
    Garante que a knowledge base do fabricante existe.
    Se não existir, constrói uma nova.

    Returns:
        Caminho para o arquivo JSON da knowledge base
    """
    kb_dir = os.path.join(OUTPUT_DIR, "knowledge_bases")
    os.makedirs(kb_dir, exist_ok=True)

    kb_file = os.path.join(kb_dir, f"{manufacturer.lower()}_kb.json")

    if os.path.exists(kb_file):
        print(f"✅ Knowledge base encontrada: {manufacturer}")
        return kb_file

    print(f"🔨 Construindo knowledge base para {manufacturer}...")
    kb_builder = KnowledgeBaseBuilder(base_url, manufacturer, max_depth=2)
    kb_builder.build()
    kb_builder.save(kb_file)
    print(f"✅ Knowledge base construída: {kb_file}")

    return kb_file


def run():
    """Executa o fluxo principal do orquestrador com scraping semântico."""
    setup_directories()
    sku_list = load_inventory()
    if not sku_list:
        return

    waves = define_waves(sku_list)

    # Inicializar módulos semânticos
    kb_dir = os.path.join(OUTPUT_DIR, "knowledge_bases")
    rag_finder = RAGFinder(kb_dir)
    semantic_scraper = SemanticScraper()

    # Mapeamento de fabricantes para URLs base (pode vir de config)
    manufacturer_urls = {
        "JINKO": "https://www.jinkosolar.com",
        "TRINA": "https://www.trinasolar.com",
        "JA": "https://www.jasolar.com",
        "LONGI": "https://www.longi.com",
        "CANADIAN": "https://www.canadiansolar.com",
        "DEYE": "https://www.deyeinverter.com",
        "GROWATT": "https://www.growatt.com",
        "FRONIUS": "https://www.fronius.com",
        "GOODWE": "https://www.goodwe.com",
        "SOLIS": "https://www.solisinverters.com",
    }

    all_results = []

    for wave_name, skus_in_wave in waves.items():
        print(f"\n--- 🚀 INICIANDO {wave_name.upper()} ---")
        if not skus_in_wave:
            print("Nenhum SKU para processar nesta onda.")
            continue

        with tqdm(
            total=len(skus_in_wave),
            desc=f"Processando {wave_name}"
        ) as pbar:
            for sku in skus_in_wave:
                pbar.set_description(f"Processando {sku}")

                # 1. Parse SKU
                sku_info = parse_sku(sku)
                manufacturer = sku_info.get("manufacturer", "").upper()
                search_query = sku_info.get("search_query", "")

                # 2. Garantir Knowledge Base
                if manufacturer in manufacturer_urls:
                    kb_file = ensure_knowledge_base(
                        manufacturer, manufacturer_urls[manufacturer]
                    )

                    # 3. Buscar URL do produto com RAG
                    product_url = rag_finder.find_best_match(manufacturer, search_query)

                    if product_url:
                        print(f"🎯 Produto encontrado: {product_url}")

                        # 4. Extrair imagens semanticamente
                        image_urls = semantic_scraper.extract_product_images(
                            product_url, sku_info
                        )

                        # 5. Download, Process & QA
                        for i, image_url in enumerate(image_urls):
                            suffix = "primary" if i == 0 else f"add_{i}"
                            image_path = os.path.join(
                                IMAGE_DIR,
                                manufacturer.lower(),
                                sku,
                                f"{sku}_{suffix}.jpg",
                            )

                            os.makedirs(os.path.dirname(image_path), exist_ok=True)

                            # Download
                            try:
                                response = requests.get(image_url, timeout=30)
                                if response.status_code == 200:
                                    temp_path = f"{image_path}.tmp"
                                    with open(temp_path, "wb") as f:
                                        f.write(response.content)

                                    # Process
                                    process_image(temp_path, image_path)

                                    # QA
                                    qa_result = qa_image(image_path)

                                    # Remove temp
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)

                                    # Record
                                    all_results.append(
                                        {
                                            "sku": sku,
                                            "manufacturer": manufacturer,
                                            "image_url": image_url,
                                            "image_path": image_path,
                                            "qa_status": qa_result["status"],
                                            "qa_score": qa_result.get("score", 0),
                                        }
                                    )
                            except Exception as e:
                                print(f"❌ Erro ao processar {image_url}: {e}")
                    else:
                        print(f"⚠️ Produto não encontrado: {sku}")
                else:
                    print(f"⚠️ URL base não configurada para {manufacturer}")

                pbar.update(1)

    # 4. Gerar relatórios
    print("\n--- 📊 GERANDO RELATÓRIOS FINAIS ---")
    if all_results:
        df_results = pd.DataFrame(all_results)

        # Salvar QA Report
        df_results.to_csv(QA_REPORT_FILE, index=False)
        print(f"✅ Relatório QA salvo: {QA_REPORT_FILE}")

        # Estatísticas
        aprovados = len(df_results[df_results["qa_status"] == "APROVADO"])
        print(f"📊 Estatísticas:")
        print(f"   Total processado: {len(df_results)}")
        print(f"   Aprovados: {aprovados}")
        print(f"   Taxa de sucesso: {aprovados/len(df_results)*100:.1f}%")

    print("✅ Processo concluído.")


if __name__ == "__main__":
    run()
