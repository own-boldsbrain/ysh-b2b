"""
Teste de Integração do Fluxo Aprimorado (Plano Comandante 360)

Valida todas as melhorias implementadas no Sprint 1:
1. Sitemap Parser + Seed URLs
2. Multi-Query RAG Search
3. Google Search Fallback
4. Playwright Browser Automation (Camada 2)

Objetivo: Taxa de sucesso > 80% na descoberta de páginas de produtos
"""

import os
import json
from pathlib import Path

from sku_parser import parse_sku
from knowledge_base_builder import KnowledgeBaseBuilder
from rag_finder import RAGFinder
from semantic_scraper import SemanticScraper
from sitemap_parser import SitemapParser
from google_search_fallback import GoogleSearchFallback


def test_sitemap_discovery():
    """Testa a descoberta de URLs via sitemap.xml"""
    print("\n" + "=" * 70)
    print("TESTE 1: Sitemap Discovery")
    print("=" * 70)

    base_url = "https://www.jinkosolar.com"
    parser = SitemapParser(base_url)

    print(f"\n🔍 Descobrindo sitemap.xml de {base_url}...")
    product_urls = parser.get_product_urls()

    print(f"\n✅ Encontradas {len(product_urls[:10])} URLs de produtos (primeiras 10):")
    for i, url in enumerate(product_urls[:5], 1):
        print(f"   {i}. {url}")

    assert len(product_urls) > 0, "❌ Nenhuma URL encontrada no sitemap"
    print("\n✅ TESTE 1 PASSOU: Sitemap parser funcionando")

    return product_urls


def test_multi_query_rag():
    """Testa busca multi-query no RAG"""
    print("\n" + "=" * 70)
    print("TESTE 2: Multi-Query RAG Search")
    print("=" * 70)

    # Parse SKU para obter queries
    sku = "PNL-JINKO-TGR-585W-NTYPE"
    print(f"\n📦 Parsing SKU: {sku}")
    parsed = parse_sku(sku)

    queries = parsed.get("search_queries", [])
    print(f"\n🔎 Queries geradas:")
    for i, q in enumerate(queries, 1):
        print(f"   {i}. {q}")

    assert len(queries) > 1, "❌ Multi-query não gerada pelo sku_parser"

    # Criar knowledge base (se não existir)
    kb_dir = Path("../output/knowledge_bases")
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "jinko_kb.json"

    if not kb_file.exists():
        print(f"\n🔨 Construindo knowledge base para JINKO...")
        builder = KnowledgeBaseBuilder(
            "https://www.jinkosolar.com", "JINKO", max_depth=2, seed_urls=[]
        )
        builder.build()
        builder.save(str(kb_file))

    # Testar RAG finder
    print(f"\n🎯 Testando multi_query_search...")
    rag = RAGFinder(str(kb_dir))
    result = rag.multi_query_search("JINKO", queries, top_k=3)

    print(f"\n✅ Resultado da busca:")
    print(f"   URL: {result['best_url']}")
    print(f"   Score: {result['score']:.4f}")
    print(f"   Queries matched: {result['queries_matched']}")

    assert result["best_url"] is not None, "❌ Nenhuma URL encontrada"
    assert result["score"] > 0, "❌ Score inválido"

    print("\n✅ TESTE 2 PASSOU: Multi-query RAG funcionando")

    return result


def test_google_fallback():
    """Testa fallback do Google Search"""
    print("\n" + "=" * 70)
    print("TESTE 3: Google Search Fallback")
    print("=" * 70)

    query = "JINKO Tiger Neo 585W datasheet"
    site = "jinkosolar.com"

    print(f"\n🔍 Buscando no Google:")
    print(f"   Query: {query}")
    print(f"   Site: {site}")

    google = GoogleSearchFallback(use_official_api=False)
    url = google.search(query, site=site)

    if url:
        print(f"\n✅ URL encontrada: {url}")
        print("\n✅ TESTE 3 PASSOU: Google fallback funcionando")
    else:
        print("\n⚠️ TESTE 3 FALHOU: Google não retornou resultados")
        print("   (Pode ser bloqueio/rate-limit)")

    return url


def test_playwright_extraction():
    """Testa extração com Playwright (SPAs)"""
    print("\n" + "=" * 70)
    print("TESTE 4: Playwright Browser Automation")
    print("=" * 70)

    # URL conhecida por ser SPA (Jinko usa React)
    test_url = "https://www.jinkosolar.com/en/site/product"

    print(f"\n🎭 Testando Playwright em: {test_url}")

    try:
        from playwright_scraper import PlaywrightScraper

        pw = PlaywrightScraper()
        result = pw.extract_with_browser(test_url)

        print(f"\n✅ Extração completa:")
        print(f"   HTML length: {len(result['html'])} chars")
        print(f"   Imagens descobertas: {len(result['images'])}")
        print(f"   API calls interceptadas: {len(result['api_data'])}")

        if result["images"]:
            print(f"\n   Primeiras 3 imagens:")
            for i, img in enumerate(result["images"][:3], 1):
                print(f"   {i}. {img}")

        assert len(result["html"]) > 0, "❌ HTML vazio"
        print("\n✅ TESTE 4 PASSOU: Playwright funcionando")

        return result

    except Exception as e:
        print(f"\n⚠️ TESTE 4 FALHOU: {e}")
        print("   (Playwright pode não estar instalado)")
        return None


def test_end_to_end_flow():
    """Teste end-to-end completo do fluxo aprimorado"""
    print("\n" + "=" * 70)
    print("TESTE 5: Fluxo End-to-End Completo")
    print("=" * 70)

    sku = "PNL-JINKO-TGR-585W-NTYPE"
    base_url = "https://www.jinkosolar.com"

    print(f"\n📦 SKU: {sku}")
    print(f"🌐 Base URL: {base_url}")

    # 1. Parse SKU
    print("\n[1/5] Parsing SKU...")
    parsed = parse_sku(sku)
    queries = parsed.get("search_queries", [])
    print(f"   ✅ {len(queries)} queries geradas")

    # 2. Sitemap Discovery
    print("\n[2/5] Descobrindo sitemap...")
    parser = SitemapParser(base_url)
    all_seed_urls = parser.get_product_urls()
    seed_urls = all_seed_urls[:20]  # Limitar a 20
    print(f"   ✅ {len(seed_urls)} seed URLs")

    # 3. Build Knowledge Base com seed URLs
    print("\n[3/5] Construindo Knowledge Base...")
    kb_dir = Path("../output/knowledge_bases")
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "jinko_enhanced_kb.json"

    if kb_file.exists():
        print(f"   ℹ️ KB já existe, pulando construção")
    else:
        builder = KnowledgeBaseBuilder(
            base_url, "JINKO", max_depth=2, seed_urls=seed_urls
        )
        builder.build()
        builder.save(str(kb_file))
        print(f"   ✅ KB salva em {kb_file}")

    # 4. Multi-Query RAG Search
    print("\n[4/5] Buscando produto com Multi-Query RAG...")
    rag = RAGFinder(str(kb_dir))
    result = rag.multi_query_search("JINKO", queries, top_k=5)

    print(f"   📊 Resultado:")
    print(f"      URL: {result['best_url']}")
    print(f"      Score: {result['score']:.4f}")
    print(f"      Queries matched: {result['queries_matched']}")

    # 5. Google Fallback se score baixo
    final_url = result["best_url"]
    if result["score"] < 0.5:
        print("\n   ⚠️ Score baixo, ativando Google fallback...")
        google = GoogleSearchFallback(use_official_api=False)
        google_url = google.search(queries[0], site="jinkosolar.com")
        if google_url:
            final_url = google_url
            print(f"   ✅ Google encontrou: {final_url}")
        else:
            print(f"   ⚠️ Google falhou, mantendo RAG: {final_url}")

    # 6. Extração Semântica com Camadas
    if final_url:
        print(f"\n[5/5] Extraindo imagens de {final_url}...")
        scraper = SemanticScraper()
        images = scraper.extract_product_images(final_url, parsed["search_query"])

        print(f"\n✅ Extração completa:")
        print(f"   Total de imagens: {len(images)}")
        if images:
            print(f"\n   Primeiras 3:")
            for i, img in enumerate(images[:3], 1):
                print(f"   {i}. {img['url']} (tipo: {img['type']})")

        success = len(images) > 0
    else:
        print("\n❌ Nenhuma URL encontrada")
        success = False

    print("\n" + "=" * 70)
    if success:
        print("✅ TESTE 5 PASSOU: Fluxo end-to-end funcionando")
    else:
        print("❌ TESTE 5 FALHOU: Nenhuma imagem extraída")
    print("=" * 70)

    return success


def run_all_tests():
    """Executa todos os testes de integração"""
    print("\n" + "=" * 70)
    print("TESTE DE INTEGRAÇÃO - PLANO COMANDANTE 360")
    print("Sprint 1: Validação das melhorias implementadas")
    print("=" * 70)

    results = {}

    try:
        results["sitemap"] = test_sitemap_discovery() is not None
    except Exception as e:
        print(f"❌ Erro no teste 1: {e}")
        results["sitemap"] = False

    try:
        results["multi_query_rag"] = test_multi_query_rag() is not None
    except Exception as e:
        print(f"❌ Erro no teste 2: {e}")
        results["multi_query_rag"] = False

    try:
        results["google_fallback"] = test_google_fallback() is not None
    except Exception as e:
        print(f"❌ Erro no teste 3: {e}")
        results["google_fallback"] = False

    try:
        results["playwright"] = test_playwright_extraction() is not None
    except Exception as e:
        print(f"❌ Erro no teste 4: {e}")
        results["playwright"] = False

    try:
        results["end_to_end"] = test_end_to_end_flow()
    except Exception as e:
        print(f"❌ Erro no teste 5: {e}")
        results["end_to_end"] = False

    # Relatório final
    print("\n" + "=" * 70)
    print("RELATÓRIO FINAL")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    print(f"\n📊 Resultados:")
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Taxa de sucesso: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed >= 4:
        print("\n✅ SPRINT 1 VALIDADO: Sistema aprimorado funcionando!")
    elif passed >= 3:
        print("\n⚠️ SPRINT 1 PARCIAL: Algumas funcionalidades falharam")
    else:
        print("\n❌ SPRINT 1 NECESSITA CORREÇÕES: Múltiplas falhas detectadas")

    print("=" * 70 + "\n")

    return results


if __name__ == "__main__":
    run_all_tests()
