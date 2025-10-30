"""
Test Script - Fluxo Semântico End-to-End

Testa o pipeline completo de scraping semântico com um único SKU.
"""

import sys
from pathlib import Path

# Adicionar scripts ao path
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_DIR, IMAGE_DIR  # noqa: E402
from sku_parser import parse_sku  # noqa: E402
from knowledge_base_builder import KnowledgeBaseBuilder  # noqa: E402
from rag_finder import RAGFinder  # noqa: E402
from semantic_scraper import SemanticScraper  # noqa: E402
from image_processor import process_image  # noqa: E402
from quality_assurance import qa_image  # noqa: E402


def test_single_sku(sku: str, manufacturer_url: str):
    """
    Testa o fluxo completo para um único SKU

    Args:
        sku: SKU do produto (ex: "PNL-JINKO-TGR-585W-NTYPE")
        manufacturer_url: URL base do fabricante
    """
    print("=" * 70)
    print("🧪 TESTE DE FLUXO SEMÂNTICO END-TO-END")
    print("=" * 70)
    print()

    # 1. Parse SKU
    print("1️⃣ PARSE DO SKU")
    print("-" * 70)
    sku_info = parse_sku(sku)
    print(f"SKU: {sku}")
    print(f"Fabricante: {sku_info.get('manufacturer')}")
    print(f"Série: {sku_info.get('series')}")
    print(f"Potência: {sku_info.get('power_watts')}W")
    print(f"Tecnologia: {sku_info.get('technology')}")
    print(f"Query de busca: {sku_info.get('search_query')}")
    print()

    # 2. Construir Knowledge Base
    print("2️⃣ CONSTRUÇÃO DA KNOWLEDGE BASE")
    print("-" * 70)
    manufacturer = sku_info.get("manufacturer", "unknown").upper()
    kb_dir = Path(OUTPUT_DIR) / "knowledge_bases"
    kb_dir.mkdir(parents=True, exist_ok=True)

    kb_file = kb_dir / f"{manufacturer.lower()}_kb.json"

    if kb_file.exists():
        print(f"✅ Knowledge base existente: {kb_file}")
    else:
        print(f"🔨 Construindo knowledge base de {manufacturer_url}...")
        kb_builder = KnowledgeBaseBuilder(manufacturer_url, manufacturer, max_depth=2)
        kb_builder.build()
        kb_builder.save(str(kb_file))
        print(f"✅ Knowledge base salva: {kb_file}")
    print()

    # 3. Busca RAG
    print("3️⃣ BUSCA SEMÂNTICA (RAG)")
    print("-" * 70)
    rag_finder = RAGFinder(str(kb_dir))

    search_query = sku_info.get("search_query", "")
    print(f"Query: {search_query}")

    # Buscar top 5 resultados
    results = rag_finder.find_product_url(manufacturer, search_query, top_k=5)

    if results:
        print(f"\n✅ {len(results)} URLs encontradas:")
        for i, (url, score) in enumerate(results, 1):
            print(f"   {i}. {url} (score: {score:.3f})")

        best_url = results[0][0]
        best_score = results[0][1]
        print(f"\n🎯 Melhor match: {best_url} (score: {best_score:.3f})")
    else:
        print("❌ Nenhuma URL encontrada")
        return
    print()

    # 4. Extração Semântica de Imagens
    print("4️⃣ EXTRAÇÃO SEMÂNTICA DE IMAGENS")
    print("-" * 70)
    semantic_scraper = SemanticScraper()

    print(f"Analisando: {best_url}")
    image_urls = semantic_scraper.extract_product_images(best_url, sku_info)

    if image_urls:
        print(f"\n✅ {len(image_urls)} imagem(ns) encontrada(s):")
        for i, img_url in enumerate(image_urls, 1):
            print(f"   {i}. {img_url}")
    else:
        print("❌ Nenhuma imagem encontrada")
        return
    print()

    # 5. Download e Processamento
    print("5️⃣ DOWNLOAD E PROCESSAMENTO")
    print("-" * 70)

    output_dir = Path(IMAGE_DIR) / manufacturer.lower() / sku
    output_dir.mkdir(parents=True, exist_ok=True)

    processed_images = []

    for i, img_url in enumerate(image_urls[:3]):  # Limitar a 3 para teste
        suffix = "primary" if i == 0 else f"add_{i}"
        output_path = output_dir / f"{sku}_{suffix}.jpg"
        temp_path = output_dir / f"{sku}_{suffix}.tmp"

        print(f"\nProcessando imagem {i+1}/{len(image_urls[:3])}")
        print(f"   URL: {img_url}")

        try:
            # Download
            import requests

            response = requests.get(img_url, timeout=30)
            response.raise_for_status()

            with open(temp_path, "wb") as f:
                f.write(response.content)

            print(f"   ✅ Download: {len(response.content)} bytes")

            # Processar
            primary_path = output_path
            secondary_path = str(output_path.parent / f"{sku}_{suffix}_600x600.jpg")
            process_image(str(temp_path), str(primary_path), secondary_path)
            print(f"   ✅ Processada: {output_path}")

            # Remover temporário
            if temp_path.exists():
                temp_path.unlink()

            processed_images.append(str(output_path))

        except requests.RequestException as e:
            print(f"   ❌ Erro: {e}")
    print()

    # 6. Quality Assurance
    print("6️⃣ QUALITY ASSURANCE")
    print("-" * 70)

    qa_results = []
    for img_path in processed_images:
        print(f"\nAnalisando: {Path(img_path).name}")
        qa_result = qa_image(img_path)

        print(f"   Status: {qa_result['status']}")
        print(f"   Dimensões: {qa_result['width']}x{qa_result['height']}")
        print(f"   Tamanho: {qa_result['size_mb']:.2f} MB")
        print(f"   Background score: {qa_result.get('bg_score', 0):.2f}")

        qa_results.append(qa_result)
    print()

    # 7. Resumo Final
    print("=" * 70)
    print("📊 RESUMO DO TESTE")
    print("=" * 70)
    print(f"SKU: {sku}")
    print(f"Produto encontrado: {'✅ Sim' if results else '❌ Não'}")
    print(f"Imagens extraídas: {len(image_urls)}")
    print(f"Imagens processadas: {len(processed_images)}")

    aprovadas = sum(1 for qa in qa_results if qa["status"] == "APROVADO")
    print(f"Imagens aprovadas: {aprovadas}/{len(qa_results)}")

    if qa_results:
        print(f"Taxa de aprovação: {aprovadas/len(qa_results)*100:.1f}%")

    print()
    print("✅ TESTE CONCLUÍDO")
    print("=" * 70)


def main():
    """Função principal do teste"""
    print("\n🧪 Teste de Fluxo Semântico\n")

    # Exemplos de SKUs para teste
    test_cases = [
        {
            "sku": "PNL-JINKO-TGR-585W-NTYPE",
            "url": "https://www.jinkosolar.com",
        },
        {"sku": "INV-DEYE-SUN-8KW-SG", "url": "https://www.deyeinverter.com"},
    ]

    print("Casos de teste disponíveis:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['sku']} ({case['url']})")
    print()

    # Executar primeiro caso por padrão
    choice = input("Escolha um caso (1-2) ou Enter para caso 1: ").strip()

    if choice == "2":
        selected = test_cases[1]
    else:
        selected = test_cases[0]

    print()
    test_single_sku(selected["sku"], selected["url"])


if __name__ == "__main__":
    main()
