"""
Test Script - Análise Avançada de Estrutura de Sites

Este script demonstra as capacidades de análise HTML/CSS,
detecção de padrões, e geração de estratégias de scraping.
"""

import sys
from advanced_scraper import AdvancedScraper, create_product_discovery_flow
from semantic_scraper import SemanticScraper


def test_structure_analysis():
    """Testa análise de estrutura de página"""
    print("=" * 70)
    print("🧪 TESTE 1: Análise de Estrutura HTML/CSS")
    print("=" * 70)

    scraper = SemanticScraper()

    # URLs de teste de diferentes fabricantes
    test_urls = [
        {
            "url": "https://www.jinkosolar.com/en/site/tigerneo",
            "name": "Jinko Tiger Neo",
        },
        {
            "url": "https://www.deyeinverter.com/product-category/inverter/",
            "name": "Deye Inverter Listing",
        },
    ]

    for test in test_urls:
        print(f"\n📍 Testando: {test['name']}")
        print(f"   URL: {test['url']}\n")

        # Busca conteúdo
        html = scraper._fetch_page_content(test["url"])
        if not html:
            print("   ❌ Falha ao buscar página")
            continue

        # Analisa estrutura
        analysis = scraper.advanced_scraper.analyze_page_structure(html, test["url"])

        # Exibe resultados
        print("\n📊 ANÁLISE CSS:")
        css = analysis["css_analysis"]
        if css["framework_detected"]:
            print(f"   Framework: {css['framework_detected']}")

        if css["component_patterns"]:
            print(f"   Componentes detectados:")
            for comp in css["component_patterns"]:
                print(f"      - {comp['type']}: {len(comp['classes'])} classes")

        print(f"\n   Classes mais usadas:")
        for cls, count in list(css["custom_classes"].most_common(5)):
            print(f"      {cls}: {count}x")

        print("\n📊 ANÁLISE HTML SEMÂNTICO:")
        semantic = analysis["html_semantic"]
        print(f"   Score de acessibilidade: {semantic['accessibility_score']}/100")

        if semantic["html5_tags"]:
            print(f"   Tags HTML5 usadas:")
            for tag, count in semantic["html5_tags"].items():
                print(f"      <{tag}>: {count}x")

        if semantic["heading_structure"]:
            print(f"   Estrutura de headings:")
            for h in semantic["heading_structure"][:3]:
                print(f"      H{h['level']}: {h['count']} encontrados")

        print("\n📊 ELEMENTOS DE NAVEGAÇÃO:")
        nav = analysis["navigation_elements"]
        print(f"   Total: {len(nav)} elementos")
        for element in nav[:3]:
            nav_type = element.get("type", "unknown")
            link_count = element.get("link_count", 0)
            print(f"      {nav_type}: {link_count} links")

        print("\n📊 ELEMENTOS INTERATIVOS:")
        interactive = analysis["interactive_elements"]
        buttons = [e for e in interactive if e["type"] == "button"]
        forms = [e for e in interactive if e["type"] == "form"]
        selects = [e for e in interactive if e["type"] == "select"]

        print(f"   Botões: {len(buttons)}")
        print(f"   Formulários: {len(forms)}")
        print(f"   Dropdowns: {len(selects)}")

        print("\n📊 FONTES DE DADOS:")
        data_sources = analysis["data_sources"]
        ajax = data_sources.get("ajax_endpoints", [])
        json_ld = data_sources.get("json_ld", [])

        if ajax:
            print(f"   ⚡ AJAX endpoints detectados: {len(ajax)}")
            for endpoint in ajax[:3]:
                print(f"      - {endpoint}")

        if json_ld:
            print(f"   📦 JSON-LD estruturado: {len(json_ld)} blocos")

        print("\n📊 PADRÕES DE LAYOUT:")
        layout = analysis["layout_patterns"]
        print(f"   Header: {'✅' if layout['has_header'] else '❌'}")
        print(f"   Footer: {'✅' if layout['has_footer'] else '❌'}")
        print(f"   Sidebar: {'✅' if layout['has_sidebar'] else '❌'}")
        print(f"   Grid: {'✅' if layout['grid_detected'] else '❌'}")
        print(f"   Cards: {'✅' if layout['cards_detected'] else '❌'}")

        # Gera estratégia
        print("\n🎯 ESTRATÉGIA DE SCRAPING GERADA:")
        strategy = scraper.advanced_scraper.generate_scraping_strategy(analysis)

        print(f"   SPA detectado: {'✅' if strategy['spa_detected'] else '❌'}")
        print(f"   Requer AJAX handling: {'✅' if strategy['ajax_handling'] else '❌'}")

        print(f"\n   📋 Tasks geradas ({len(strategy['tasks'])}):")
        for task in strategy["tasks"]:
            print(f"      - {task['task']} ({task['method']})")

        print(f"\n   🎯 Seletores sugeridos:")
        for key, selectors in strategy["selectors"].items():
            if selectors:
                print(f"      {key}: {len(selectors)} seletores")
                for sel in selectors[:2]:
                    print(f"         • {sel}")

        print("\n" + "=" * 70)


def test_navigation_flow():
    """Testa criação de fluxo de navegação"""
    print("\n\n" + "=" * 70)
    print("🧪 TESTE 2: Fluxo de Navegação (Steps & Tasks)")
    print("=" * 70 + "\n")

    # Cria fluxo padrão
    flow = create_product_discovery_flow("https://www.jinkosolar.com")

    print(f"📋 Fluxo: {flow.name}")
    print(f"   Total de Steps: {len(flow.steps)}")
    print(f"   Total de Tasks: {len(flow.tasks)}")

    print("\n📍 STEPS:")
    for step in flow.steps:
        step_num = step.get("step_number", "?")
        action = step.get("action", "unknown")
        desc = step.get("description", "")
        print(f"\n   Step {step_num}: {action}")
        print(f"      Descrição: {desc}")

        if "selectors" in step:
            print(f"      Seletores:")
            for sel in step["selectors"][:3]:
                print(f"         • {sel}")

        if "expected_elements" in step:
            print(f"      Elementos esperados: {', '.join(step['expected_elements'])}")

    print("\n✅ TASKS:")
    for task in flow.tasks:
        task_name = task.get("task", "unknown")
        priority = task.get("priority", "normal")
        print(f"\n   Task: {task_name} [prioridade: {priority}]")

        if "fields" in task:
            print(f"      Campos: {', '.join(task['fields'])}")

        if "methods" in task:
            print(f"      Métodos ({len(task['methods'])}):")
            for method in task["methods"]:
                print(f"         • {method['type']}: {method['selector']}")

        if "selectors" in task and isinstance(task["selectors"], list):
            print(f"      Seletores:")
            for sel in task["selectors"][:3]:
                print(f"         • {sel}")

    print("\n" + "=" * 70)


def main():
    """Executa todos os testes"""
    print("\n🚀 ADVANCED SCRAPER - TESTES DE ANÁLISE DE ESTRUTURA\n")

    # Teste 1: Análise de estrutura
    test_structure_analysis()

    # Teste 2: Fluxo de navegação
    test_navigation_flow()

    print("\n\n✅ Todos os testes concluídos!\n")


if __name__ == "__main__":
    main()
