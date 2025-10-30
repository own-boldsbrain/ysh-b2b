"""Testes de integração e benchmarks para sistema de fallbacks.

Valida:
- Funcionalidade de cada camada
- Performance comparativa
- Comportamento de circuit breaker
- Adaptive thresholds
- Integração end-to-end
"""

import time
from pathlib import Path

from intelligent_fallback_orchestrator import IntelligentFallbackOrchestrator
from ollama_fallback import OllamaFallback
from rag_finder import RAGFinder
from searx_fallback import SearxFallback


def test_ollama_fallback():
    """Testa Ollama com cache e circuit breaker."""
    print("\n" + "=" * 70)
    print("TESTE 1: Ollama Fallback (cache, retry, circuit breaker)")
    print("=" * 70)

    ollama = OllamaFallback(
        cache_ttl=300,
        max_retries=2,
        enable_cache=True,
    )

    # Teste 1: primeira chamada (miss cache)
    print("\n[1.1] Primeira chamada (cache miss)")
    url1 = ollama.suggest_url(
        base_domain="https://jinkosolar.com",
        product_name="Tiger Neo 585W JKM585N-72HL4-V",
        product_context="Painel fotovoltaico monocristalino N-Type",
    )
    print(f"   URL: {url1}")

    # Teste 2: segunda chamada (cache hit)
    print("\n[1.2] Segunda chamada (cache hit esperado)")
    start = time.time()
    url2 = ollama.suggest_url(
        base_domain="https://jinkosolar.com",
        product_name="Tiger Neo 585W JKM585N-72HL4-V",
    )
    latency = (time.time() - start) * 1000
    print(f"   URL: {url2}")
    print(f"   Latência: {latency:.2f}ms (deve ser < 10ms)")

    assert url1 == url2, "Cache deveria retornar mesma URL"
    assert latency < 50, "Cache deveria ser muito rápido"

    # Teste 3: métricas
    print("\n[1.3] Métricas")
    metrics = ollama.get_metrics()
    print(f"   Total requests: {metrics['total_requests']}")
    print(f"   Cache hit rate: {metrics['cache_hit_rate']:.1%}")
    print(f"   Success rate: {metrics['success_rate']:.1%}")
    print(f"   Avg latency: {metrics['avg_latency_ms']:.0f}ms")

    assert metrics["cache_hit_rate"] > 0, "Deveria ter cache hit"

    print("\n✅ TESTE 1 PASSOU")


def test_searx_fallback():
    """Testa SearxNG com scoring e filtros."""
    print("\n" + "=" * 70)
    print("TESTE 2: SearxNG Fallback (scoring, filtros, cache)")
    print("=" * 70)

    searx = SearxFallback(enable_cache=True, cache_ttl=300)

    # Teste 1: busca básica
    print("\n[2.1] Busca básica")
    results = searx.search(
        query="Jinko Tiger Neo 585W datasheet",
        site="jinkosolar.com",
        max_results=5,
    )

    print(f"   Resultados: {len(results)}")
    for i, r in enumerate(results[:3], 1):
        print(f"   {i}. [{r.score:.3f}] {r.title[:50]} " f"(engine: {r.engine})")

    assert len(results) > 0, "Deveria retornar resultados"
    assert all(r.score >= 0 for r in results), "Scores inválidos"

    # Teste 2: cache
    print("\n[2.2] Cache")
    start = time.time()
    results2 = searx.search(
        query="Jinko Tiger Neo 585W datasheet",
        site="jinkosolar.com",
        max_results=5,
    )
    latency = (time.time() - start) * 1000

    print(f"   Latência: {latency:.2f}ms")
    assert results == results2, "Cache deveria retornar mesmos resultados"

    # Teste 3: métricas
    print("\n[2.3] Métricas")
    metrics = searx.get_metrics()
    print(f"   Total requests: {metrics['total_requests']}")
    print(f"   Cache hit rate: {metrics['cache_hit_rate']:.1%}")
    print(f"   Success rate: {metrics['success_rate']:.1%}")

    print("\n✅ TESTE 2 PASSOU")


def test_rag_finder():
    """Testa RAG com multi-query."""
    print("\n" + "=" * 70)
    print("TESTE 3: RAG Finder (multi-query)")
    print("=" * 70)

    kb_dir = Path("../output/knowledge_bases")
    if not kb_dir.exists():
        print("⚠️  Knowledge base não encontrada, pulando teste")
        return

    rag = RAGFinder(str(kb_dir))

    queries = [
        "JKM585N-72HL4-V",
        "Tiger Neo 585W",
        "Jinko 585 Watt panel",
    ]

    print(f"\n[3.1] Multi-query search ({len(queries)} queries)")
    result = rag.multi_query_search("JINKO", queries, top_k=5)

    print(f"   Best URL: {result.get('best_url')}")
    print(f"   Score: {result.get('score', 0):.3f}")
    print(f"   Queries matched: {result.get('queries_matched', 0)}")

    assert result.get("best_url"), "Deveria encontrar URL"
    assert result.get("score", 0) > 0, "Score deveria ser > 0"

    print("\n✅ TESTE 3 PASSOU")


def test_intelligent_orchestrator():
    """Testa orquestrador inteligente end-to-end."""
    print("\n" + "=" * 70)
    print("TESTE 4: Intelligent Orchestrator (adaptive, circuit breaker)")
    print("=" * 70)

    kb_dir = Path("../output/knowledge_bases")
    if not kb_dir.exists():
        print("⚠️  Knowledge base não encontrada, pulando teste")
        return

    orchestrator = IntelligentFallbackOrchestrator(
        kb_dir=kb_dir,
        circuit_threshold=3,
        enable_adaptive=True,
    )

    # Teste 1: busca normal
    print("\n[4.1] Busca normal (deve usar RAG)")
    result = orchestrator.search(
        manufacturer="JINKO",
        product_name="Tiger Neo 585W JKM585N-72HL4-V",
        base_domain="https://jinkosolar.com",
        queries=[
            "JKM585N-72HL4-V",
            "Tiger Neo 585W",
            "Jinko 585 monocristalino",
        ],
    )

    if result:
        print(f"   URL: {result.url}")
        print(f"   Score: {result.score:.3f}")
        print(f"   Layer: {result.layer.value}")
        assert result.url, "URL deveria ser retornada"
    else:
        print("   ⚠️  Nenhum resultado (RAG pode ter score baixo)")

    # Teste 2: health check
    print("\n[4.2] Health Check")
    health = orchestrator.health_check()
    for layer, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {layer}: {'OK' if status else 'FALHOU'}")

    # Teste 3: métricas por camada
    print("\n[4.3] Métricas por camada")
    metrics = orchestrator.get_metrics()
    for layer, m in metrics.items():
        print(f"\n   {layer.upper()}:")
        print(f"      Requests: {m['total_requests']}")
        print(f"      Success rate: {m['success_rate']:.1%}")
        print(f"      Avg latency: {m['avg_latency_ms']:.0f}ms")
        print(f"      Circuit open: {m['circuit_open']}")

    # Teste 4: configuração adaptativa
    print("\n[4.4] Configuração Adaptativa")
    config = orchestrator.get_config()
    for key, value in config.items():
        print(f"   {key}: {value}")

    print("\n✅ TESTE 4 PASSOU")


def benchmark_layers():
    """Benchmark comparativo das três camadas."""
    print("\n" + "=" * 70)
    print("TESTE 5: Benchmark Comparativo")
    print("=" * 70)

    kb_dir = Path("../output/knowledge_bases")
    if not kb_dir.exists():
        print("⚠️  KB não encontrada")
        return

    orchestrator = IntelligentFallbackOrchestrator(kb_dir=kb_dir)

    test_cases = [
        {
            "manufacturer": "JINKO",
            "product": "Tiger Neo 585W",
            "domain": "https://jinkosolar.com",
            "queries": ["Tiger Neo 585", "JKM585N"],
        },
    ]

    print("\nExecutando busca em todas as camadas...\n")

    for i, case in enumerate(test_cases, 1):
        print(f"Caso {i}: {case['product']}")

        result = orchestrator.search(
            manufacturer=case["manufacturer"],
            product_name=case["product"],
            base_domain=case["domain"],
            queries=case["queries"],
        )

        if result:
            print(f"   ✅ {result.layer.value}: {result.url[:60]}...")
        else:
            print("   ❌ Nenhuma camada retornou resultado")

    # Métricas finais
    print("\n📊 Resumo de Performance:\n")
    metrics = orchestrator.get_metrics()
    for layer, m in metrics.items():
        if m["total_requests"] > 0:
            print(f"{layer.upper()}:")
            print(f"   Success: {m['success_rate']:.0%}")
            print(f"   Latency: {m['avg_latency_ms']:.0f}ms")
            print()

    print("✅ BENCHMARK COMPLETO")


def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("SUITE DE TESTES - SISTEMA DE FALLBACKS FOSS")
    print("=" * 70)

    try:
        test_ollama_fallback()
    except Exception as e:
        print(f"\n❌ Teste 1 falhou: {e}")

    try:
        test_searx_fallback()
    except Exception as e:
        print(f"\n❌ Teste 2 falhou: {e}")

    try:
        test_rag_finder()
    except Exception as e:
        print(f"\n❌ Teste 3 falhou: {e}")

    try:
        test_intelligent_orchestrator()
    except Exception as e:
        print(f"\n❌ Teste 4 falhou: {e}")

    try:
        benchmark_layers()
    except Exception as e:
        print(f"\n❌ Benchmark falhou: {e}")

    print("\n" + "=" * 70)
    print("TESTES CONCLUÍDOS")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
