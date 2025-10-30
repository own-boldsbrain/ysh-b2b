"""
Orquestrador Principal do Plano "Comandante A"

Este script gerencia o fluxo completo de captura de imagens:
1. Lê os SKUs do inventário.
2. Organiza a execução em ondas, conforme o plano.
3. Para cada SKU, invoca os módulos de scraping, processamento e QA.
4. Gera os relatórios finais e o feed para o Meta Commerce.
"""

import os
import json
import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from config import (
    INVENTORY_FILE,
    OUTPUT_DIR,
    IMAGE_DIR,
    REPORTS_DIR,
    QA_REPORT_FILE,
)
from sku_parser import parse_sku
from image_processor import process_image
from quality_assurance import qa_image
from knowledge_base_builder import KnowledgeBaseBuilder
from rag_finder import RAGFinder
from semantic_scraper import SemanticScraper
from sitemap_parser import SitemapParser
from google_search_fallback import GoogleSearchFallback
from playwright_scraper import PlaywrightScraper


def setup_directories():
    """Cria os diretórios necessários para armazenar outputs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "knowledge_bases"), exist_ok=True)


def load_inventory():
    """Carrega a lista de SKUs do inventário."""
    if not os.path.exists(INVENTORY_FILE):
        print(
            f"❌ Erro: Arquivo de inventário não encontrado em " f"'{INVENTORY_FILE}'"
        )
        return []

    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    skus = [item["sku"] for item in data]
    print(f"✅ {len(skus)} SKUs carregados do inventário.")
    return skus


def define_waves(sku_list):
    """Define as ondas de execução conforme o plano."""
    wave_1 = [
        "PNL-JINKO-TGR-585W-NTYPE",
        "PNL-TRINA-VERTEX-670W",
        "PNL-JA-JAM72-550W",
        "PNL-LONGI-HMO6-665W",
        "PNL-CANA-CS7N-550W",
        "INV-DEYE-SUN-8KW-SG",
    ]

    wave_2 = [sku for sku in sku_list if sku.startswith("PNL-") and sku not in wave_1]
    wave_3 = [sku for sku in sku_list if sku.startswith("INV-") and sku not in wave_1]

    waves = {"wave1": wave_1, "wave2": wave_2, "wave3": wave_3}
    print(
        f"🌊 Ondas de execução definidas: "
        f"{len(waves['wave1'])} na Onda 1, "
        f"{len(waves['wave2'])} na Onda 2, "
        f"{len(waves['wave3'])} na Onda 3."
    )
    return waves


def ensure_knowledge_base(manufacturer: str, base_url: str) -> str:
    """
    Garante que a knowledge base do fabricante existe.
    Se não existir, constrói uma nova usando seed URLs do sitemap.

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

    # 🆕 Descobrir seed URLs do sitemap
    sitemap_parser = SitemapParser(base_url)
    seed_urls = sitemap_parser.get_product_urls()
    print(f"   📍 {len(seed_urls)} seed URLs descobertas do sitemap")

    # Construir KB com seed URLs
    kb_builder = KnowledgeBaseBuilder(
        base_url, manufacturer, max_depth=2, seed_urls=seed_urls
    )
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

    # Mapeamento de fabricantes para URLs base
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

        with tqdm(total=len(skus_in_wave), desc=f"Processando {wave_name}") as pbar:
            for sku in skus_in_wave:
                pbar.set_description(f"Processando {sku}")

                # 1. Parse SKU
                sku_info = parse_sku(sku)
                manufacturer = sku_info.get("manufacturer", "").upper()
                search_queries = sku_info.get("search_queries", [])
                search_query = sku_info.get("search_query", "")  # fallback single query

                # 2. Garantir Knowledge Base
                if manufacturer in manufacturer_urls:
                    ensure_knowledge_base(manufacturer, manufacturer_urls[manufacturer])

                    # 3. Buscar URL do produto com Multi-Query RAG
                    if search_queries:
                        result = rag_finder.multi_query_search(
                            manufacturer, search_queries, top_k=3
                        )
                        product_url = result["best_url"]
                        confidence_score = result["score"]
                        print(f"   🎯 RAG Score: {confidence_score:.2f}")

                        # 🆕 Google Fallback se confiança baixa
                        if confidence_score < 0.5:
                            print("   ⚠️ Score baixo, tentando Google Search...")
                            google_fallback = GoogleSearchFallback(
                                use_official_api=False
                            )
                            from urllib.parse import urlparse

                            site_domain = urlparse(
                                manufacturer_urls[manufacturer]
                            ).netloc
                            google_url = google_fallback.search(
                                query=search_queries[0], site=site_domain
                            )
                            if google_url:
                                product_url = google_url
                                print(f"   ✅ Google encontrou: {product_url}")
                    else:
                        # Fallback para busca antiga (single query)
                        product_url = rag_finder.find_best_match(
                            manufacturer, search_query
                        )
                        confidence_score = 0.0

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

                                    # Process (imagem única)
                                    primary_path = image_path
                                    secondary_path = image_path.replace(
                                        ".jpg", "_600x600.jpg"
                                    )
                                    process_image(
                                        temp_path, primary_path, secondary_path
                                    )

                                    # QA
                                    qa_result = qa_image(primary_path)

                                    # Remove temp
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)

                                    # Record
                                    all_results.append(
                                        {
                                            "sku": sku,
                                            "manufacturer": manufacturer,
                                            "image_url": image_url,
                                            "image_path": primary_path,
                                            "qa_status": qa_result["status"],
                                            "qa_score": qa_result.get("score", 0),
                                        }
                                    )
                            except requests.RequestException as e:
                                print(f"❌ Erro ao processar " f"{image_url}: {e}")
                    else:
                        print(f"⚠️ Produto não encontrado: {sku}")
                else:
                    print(f"⚠️ URL base não configurada para " f"{manufacturer}")

                pbar.update(1)

    # Gerar relatórios
    print("\n--- 📊 GERANDO RELATÓRIOS FINAIS ---")
    if all_results:
        df_results = pd.DataFrame(all_results)

        # Salvar QA Report
        df_results.to_csv(QA_REPORT_FILE, index=False)
        print(f"✅ Relatório QA salvo: {QA_REPORT_FILE}")

        # Estatísticas
        aprovados = len(df_results[df_results["qa_status"] == "APROVADO"])
        print("📊 Estatísticas:")
        print(f"   Total processado: {len(df_results)}")
        print(f"   Aprovados: {aprovados}")
        print(f"   Taxa de sucesso: " f"{aprovados/len(df_results)*100:.1f}%")

    print("✅ Processo concluído.")


if __name__ == "__main__":
    run()
