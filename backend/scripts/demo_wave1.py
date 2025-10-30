"""
Script de Demonstração e Teste do Fluxo Completo

Este script executa um exemplo completo do fluxo de captura de imagens,
desde a leitura do SKU até o processamento final e QA.
"""

import os
import sys

# Adiciona o diretório scripts ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sku_parser import parse_sku
from image_scraper import ImageScraper
from pdf_extractor import extract_first_page_as_image
from image_processor import process_image
from quality_assurance import qa_image


def demo_single_sku(sku: str):
    """
    Demonstra o processamento completo de um único SKU.

    Args:
        sku (str): O SKU do produto a ser processado.
    """
    print(f"\n{'='*80}")
    print(f"DEMONSTRAÇÃO: Processamento do SKU {sku}")
    print(f"{'='*80}\n")

    # Passo 1: Parse do SKU
    print("📋 PASSO 1: Parsing do SKU")
    sku_info = parse_sku(sku)
    print(f"   Tipo: {sku_info.get('type')}")
    print(f"   Fabricante: {sku_info.get('manufacturer')}")
    print(f"   Série/Modelo: {sku_info.get('series', sku_info.get('model'))}")
    print(f"   Query de busca: {sku_info.get('search_query')}")

    # Passo 2: Buscar imagens/PDFs
    print("\n🔍 PASSO 2: Buscando imagens/PDFs oficiais")
    scraper = ImageScraper()
    candidates = scraper.find_images(sku_info)

    if not candidates:
        print("   ⚠️  Nenhuma imagem/PDF encontrado para este SKU.")
        return

    print(f"   Encontrados: {len(candidates)} item(ns)")
    for idx, candidate in enumerate(candidates, 1):
        print(f"   {idx}. [{candidate['type'].upper()}] {candidate['url']}")
        print(f"      Primary: {candidate['is_primary']}")

    # Passo 3: Processar o primeiro candidato (primário)
    print("\n⬇️  PASSO 3: Download e Extração")
    primary_candidate = candidates[0]

    # Criar diretórios temporários
    temp_dir = "output/temp"
    os.makedirs(temp_dir, exist_ok=True)

    brand = sku_info.get("manufacturer", "unknown").lower()
    output_dir = f"output/images/{brand}/{sku}"
    os.makedirs(output_dir, exist_ok=True)

    # Download
    file_ext = ".pdf" if primary_candidate["type"] == "pdf" else ".png"
    temp_download = os.path.join(temp_dir, f"{sku}_demo{file_ext}")

    if not scraper.download_file(primary_candidate["url"], temp_download):
        print("   ❌ Falha no download. Encerrando demonstração.")
        return

    # Extração (se PDF)
    if primary_candidate["type"] == "pdf":
        print("\n📄 PASSO 4: Extraindo imagem do PDF")
        temp_extracted = os.path.join(temp_dir, f"{sku}_demo_extracted.png")
        if not extract_first_page_as_image(temp_download, temp_extracted, dpi=300):
            print("   ❌ Falha na extração. Encerrando demonstração.")
            return
        source_image = temp_extracted
    else:
        source_image = temp_download

    # Processamento
    print("\n🎨 PASSO 5: Processamento e Normalização")
    output_primary = os.path.join(output_dir, f"{sku}_primary_1024.jpg")
    output_secondary = os.path.join(output_dir, f"{sku}_primary_600.jpg")

    process_image(source_image, output_primary, output_secondary)

    # QA
    print("\n✅ PASSO 6: Quality Assurance")
    qa_result = qa_image(output_primary)

    print(f"   Status: {qa_result.get('status')}")
    if qa_result.get("status") == "APROVADO":
        print(f"   ✅ Dimensões: {qa_result.get('width')}x{qa_result.get('height')}")
        print(f"   ✅ Tamanho: {qa_result.get('size_mb')} MB")
        print(f"   ✅ Formato: {qa_result.get('format')}")
        print(f"   ✅ Score de fundo neutro: {qa_result.get('bg_score')}%")
    else:
        print(f"   ⚠️  Motivo: {qa_result.get('reason')}")

    print("\n📊 RESULTADO FINAL")
    print(f"   Imagem principal: {output_primary}")
    print(f"   Imagem secundária: {output_secondary}")
    print(f"   Status QA: {qa_result.get('status')}")

    print(f"\n{'='*80}")
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Lista de SKUs da Onda 1 para demonstração
    wave1_skus = [
        "PNL-JINKO-TGR-585W-NTYPE",
        "PNL-TRINA-VERTEX-670W-MONO",
        "PNL-JA-JAM72-550W-PERC",
        "PNL-LONGI-HMO6-665W-BF",
        "PNL-CANA-CS7N-550W-BF",
        "INV-DEYE-SUN-8K-SG04LP3-EU",
    ]

    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO DO SISTEMA DE CAPTURA DE IMAGENS - ONDA 1")
    print("=" * 80)
    print("\nSKUs disponíveis para teste:")
    for i, sku in enumerate(wave1_skus, 1):
        print(f"{i}. {sku}")

    print(
        "\nEscolha um SKU para processar (1-6) ou pressione Enter para processar o primeiro:"
    )
    choice = input("> ").strip()

    if choice == "":
        selected_sku = wave1_skus[0]
    elif choice.isdigit() and 1 <= int(choice) <= len(wave1_skus):
        selected_sku = wave1_skus[int(choice) - 1]
    else:
        print("Opção inválida. Usando o primeiro SKU.")
        selected_sku = wave1_skus[0]

    demo_single_sku(selected_sku)
