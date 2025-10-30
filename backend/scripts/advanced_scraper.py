"""
Advanced Scraper - Raspagem Avançada com Análise de Steps e Tasks

Este módulo implementa técnicas avançadas de web scraping incluindo:
- Análise de fluxos de navegação (steps)
- Identificação de tasks de interação
- Detecção de carregamento dinâmico (AJAX/SPA)
- Análise de estrutura CSS e HTML semântico
"""

import re
import time
import json
from typing import Dict, List, Tuple, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict, Counter


class NavigationFlow:
    """Representa um fluxo de navegação no site"""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[Dict] = []
        self.tasks: List[Dict] = []
        self.success_rate: float = 0.0

    def add_step(self, step: Dict):
        """Adiciona um step ao fluxo"""
        self.steps.append(step)

    def add_task(self, task: Dict):
        """Adiciona uma task ao fluxo"""
        self.tasks.append(task)


class AdvancedScraper:
    """Scraper avançado com análise de estrutura e fluxos"""

    def __init__(self):
        self.flows: Dict[str, NavigationFlow] = {}
        self.css_patterns: Dict[str, Counter] = defaultdict(Counter)
        self.interaction_points: List[Dict] = []
        self.ajax_endpoints: Set[str] = set()

    def analyze_page_structure(self, html: str, url: str) -> Dict:
        """
        Analisa a estrutura completa de uma página HTML

        Returns:
            Dict com análises de CSS, HTML semântico, e padrões
        """
        soup = BeautifulSoup(html, "html.parser")

        analysis = {
            "url": url,
            "css_analysis": self._analyze_css_structure(soup),
            "html_semantic": self._analyze_html_semantics(soup),
            "navigation_elements": self._detect_navigation_elements(soup),
            "interactive_elements": self._detect_interactive_elements(soup),
            "data_sources": self._detect_data_sources(soup),
            "layout_patterns": self._detect_layout_patterns(soup),
        }

        return analysis

    def _analyze_css_structure(self, soup: BeautifulSoup) -> Dict:
        """Analisa estrutura CSS da página"""
        css_analysis = {
            "grid_layouts": [],
            "flex_containers": [],
            "custom_classes": Counter(),
            "framework_detected": None,
            "component_patterns": [],
        }

        # Detecta frameworks CSS
        frameworks = {
            "bootstrap": ["container", "row", "col-", "btn"],
            "tailwind": ["flex", "grid", "w-", "h-", "p-", "m-"],
            "materialize": ["material-", "mdl-", "mdc-"],
            "bulma": ["columns", "column", "section", "hero"],
        }

        all_classes = []
        for tag in soup.find_all(class_=True):
            classes = tag.get("class", [])
            all_classes.extend(classes)
            css_analysis["custom_classes"].update(classes)

        # Detecta framework
        for framework, indicators in frameworks.items():
            matches = sum(
                1 for cls in all_classes if any(ind in cls for ind in indicators)
            )
            if matches > 10:
                css_analysis["framework_detected"] = framework
                break

        # Detecta layouts CSS Grid e Flexbox
        for tag in soup.find_all(style=True):
            style = tag.get("style", "")
            if "display: grid" in style or "display:grid" in style:
                css_analysis["grid_layouts"].append(
                    {
                        "tag": tag.name,
                        "class": " ".join(tag.get("class", [])),
                        "children": len(tag.find_all(recursive=False)),
                    }
                )
            if "display: flex" in style or "display:flex" in style:
                css_analysis["flex_containers"].append(
                    {"tag": tag.name, "class": " ".join(tag.get("class", []))}
                )

        # Identifica componentes por padrões de classes
        component_patterns = [
            ("card", ["card", "product-card", "item-card"]),
            ("gallery", ["gallery", "image-grid", "photo-gallery"]),
            ("carousel", ["carousel", "slider", "swiper"]),
            ("modal", ["modal", "dialog", "popup"]),
            ("dropdown", ["dropdown", "select", "menu"]),
        ]

        for component, patterns in component_patterns:
            matches = [
                cls for cls in all_classes if any(p in cls.lower() for p in patterns)
            ]
            if matches:
                css_analysis["component_patterns"].append(
                    {"type": component, "classes": matches[:5]}
                )

        return css_analysis

    def _analyze_html_semantics(self, soup: BeautifulSoup) -> Dict:
        """Analisa HTML semântico e acessibilidade"""
        semantics = {
            "html5_tags": Counter(),
            "aria_labels": [],
            "landmark_roles": [],
            "heading_structure": [],
            "accessibility_score": 0,
        }

        # Tags semânticas HTML5
        semantic_tags = [
            "header",
            "nav",
            "main",
            "article",
            "section",
            "aside",
            "footer",
            "figure",
            "figcaption",
        ]

        for tag in semantic_tags:
            count = len(soup.find_all(tag))
            if count > 0:
                semantics["html5_tags"][tag] = count

        # ARIA labels e roles
        for tag in soup.find_all(attrs={"aria-label": True}):
            semantics["aria_labels"].append(
                {
                    "tag": tag.name,
                    "label": tag.get("aria-label"),
                    "role": tag.get("role"),
                }
            )

        for tag in soup.find_all(attrs={"role": True}):
            role = tag.get("role")
            if role in ["navigation", "main", "complementary", "contentinfo"]:
                semantics["landmark_roles"].append(role)

        # Estrutura de headings
        for level in range(1, 7):
            headings = soup.find_all(f"h{level}")
            if headings:
                semantics["heading_structure"].append(
                    {
                        "level": level,
                        "count": len(headings),
                        "samples": [h.get_text(strip=True)[:50] for h in headings[:3]],
                    }
                )

        # Score de acessibilidade básico
        score = 0
        if semantics["html5_tags"]:
            score += 30
        if semantics["aria_labels"]:
            score += 20
        if semantics["landmark_roles"]:
            score += 20
        if semantics["heading_structure"]:
            score += 30

        semantics["accessibility_score"] = score

        return semantics

    def _detect_navigation_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Detecta elementos de navegação e menu"""
        nav_elements = []

        # Navegação por tag <nav>
        for nav in soup.find_all("nav"):
            links = nav.find_all("a")
            nav_elements.append(
                {
                    "type": "nav_tag",
                    "class": " ".join(nav.get("class", [])),
                    "link_count": len(links),
                    "links": [
                        {"text": a.get_text(strip=True), "href": a.get("href")}
                        for a in links[:10]
                    ],
                }
            )

        # Navegação por role="navigation"
        for nav in soup.find_all(attrs={"role": "navigation"}):
            links = nav.find_all("a")
            nav_elements.append(
                {"type": "role_navigation", "tag": nav.name, "link_count": len(links)}
            )

        # Breadcrumbs
        breadcrumb_patterns = ["breadcrumb", "breadcrumbs", "path"]
        for pattern in breadcrumb_patterns:
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                links = element.find_all("a")
                if links:
                    nav_elements.append(
                        {
                            "type": "breadcrumb",
                            "path": [a.get_text(strip=True) for a in links],
                        }
                    )

        return nav_elements

    def _detect_interactive_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Detecta elementos interativos (botões, forms, inputs)"""
        interactive = []

        # Botões
        buttons = soup.find_all(["button", "input"], type=["button", "submit"])
        buttons.extend(soup.find_all("a", class_=re.compile(r"btn|button", re.I)))

        for btn in buttons:
            interactive.append(
                {
                    "type": "button",
                    "tag": btn.name,
                    "text": btn.get_text(strip=True) or btn.get("value", ""),
                    "class": " ".join(btn.get("class", [])),
                    "onclick": btn.get("onclick"),
                    "href": btn.get("href"),
                }
            )

        # Formulários
        for form in soup.find_all("form"):
            inputs = form.find_all(["input", "select", "textarea"])
            interactive.append(
                {
                    "type": "form",
                    "action": form.get("action"),
                    "method": form.get("method", "get"),
                    "input_count": len(inputs),
                    "inputs": [
                        {"type": i.get("type", "text"), "name": i.get("name")}
                        for i in inputs
                    ],
                }
            )

        # Dropdowns/Selects
        for select in soup.find_all("select"):
            options = select.find_all("option")
            interactive.append(
                {
                    "type": "select",
                    "name": select.get("name"),
                    "option_count": len(options),
                    "options": [opt.get_text(strip=True) for opt in options[:10]],
                }
            )

        return interactive

    def _detect_data_sources(self, soup: BeautifulSoup) -> Dict:
        """Detecta fontes de dados (API calls, AJAX, data attributes)"""
        data_sources = {
            "ajax_endpoints": [],
            "api_urls": [],
            "data_attributes": Counter(),
            "json_ld": [],
            "websockets": [],
        }

        # Scripts que podem conter endpoints
        for script in soup.find_all("script"):
            script_content = script.string or ""

            # Detecta chamadas AJAX/Fetch
            ajax_patterns = [
                r'fetch\([\'"]([^\'"]+)[\'"]',
                r'\.ajax\({[^}]*url:\s*[\'"]([^\'"]+)[\'"]',
                r'axios\.[get|post]+\([\'"]([^\'"]+)[\'"]',
                r'XMLHttpRequest.*open\([\'"][^\'"]*, [\'"]([^\'"]+)[\'"]',
            ]

            for pattern in ajax_patterns:
                matches = re.findall(pattern, script_content, re.I)
                data_sources["ajax_endpoints"].extend(matches)

            # Detecta WebSockets
            ws_pattern = r'new WebSocket\([\'"]([^\'"]+)[\'"]'
            ws_matches = re.findall(ws_pattern, script_content)
            data_sources["websockets"].extend(ws_matches)

        # JSON-LD (structured data)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                json_data = json.loads(script.string)
                data_sources["json_ld"].append(json_data)
            except:
                pass

        # Data attributes
        for tag in soup.find_all(
            attrs=lambda x: x and any(k.startswith("data-") for k in x)
        ):
            for attr in tag.attrs:
                if attr.startswith("data-"):
                    data_sources["data_attributes"][attr] += 1

        return data_sources

    def _detect_layout_patterns(self, soup: BeautifulSoup) -> Dict:
        """Detecta padrões de layout e estrutura de página"""
        patterns = {
            "has_sidebar": False,
            "has_header": False,
            "has_footer": False,
            "content_structure": None,
            "grid_detected": False,
            "cards_detected": False,
        }

        # Header
        header = soup.find("header") or soup.find(attrs={"role": "banner"})
        patterns["has_header"] = header is not None

        # Footer
        footer = soup.find("footer") or soup.find(attrs={"role": "contentinfo"})
        patterns["has_footer"] = footer is not None

        # Sidebar
        sidebar_indicators = ["sidebar", "aside", "complementary"]
        for indicator in sidebar_indicators:
            if soup.find(class_=re.compile(indicator, re.I)) or soup.find(
                attrs={"role": indicator}
            ):
                patterns["has_sidebar"] = True
                break

        # Estrutura de conteúdo
        main = soup.find("main") or soup.find(attrs={"role": "main"})
        if main:
            sections = main.find_all("section")
            articles = main.find_all("article")
            patterns["content_structure"] = {
                "sections": len(sections),
                "articles": len(articles),
                "type": (
                    "sectioned" if sections else "article-based" if articles else "flat"
                ),
            }

        # Cards (padrão comum em product pages)
        card_patterns = ["card", "product-item", "item", "box"]
        card_count = 0
        for pattern in card_patterns:
            card_count += len(soup.find_all(class_=re.compile(pattern, re.I)))
        patterns["cards_detected"] = card_count > 3

        # Grid layout
        grid_classes = ["grid", "row", "flex", "columns"]
        for cls in grid_classes:
            if soup.find(class_=re.compile(cls, re.I)):
                patterns["grid_detected"] = True
                break

        return patterns

    def create_navigation_flow(self, name: str, start_url: str) -> NavigationFlow:
        """
        Cria um fluxo de navegação para rastrear steps

        Args:
            name: Nome do fluxo (ex: "product_search")
            start_url: URL inicial
        """
        flow = NavigationFlow(name)

        # Step 1: Landing
        flow.add_step(
            {
                "step_number": 1,
                "action": "navigate",
                "url": start_url,
                "description": "Acessar página inicial",
                "expected_elements": ["nav", "search", "menu"],
            }
        )

        self.flows[name] = flow
        return flow

    def add_step_to_flow(self, flow_name: str, step: Dict):
        """Adiciona um step a um fluxo existente"""
        if flow_name in self.flows:
            step["step_number"] = len(self.flows[flow_name].steps) + 1
            self.flows[flow_name].add_step(step)

    def generate_scraping_strategy(self, analysis: Dict) -> Dict:
        """
        Gera estratégia de scraping baseada na análise

        Returns:
            Dict com estratégia de steps, tasks e seletores
        """
        strategy = {
            "steps": [],
            "tasks": [],
            "selectors": {"products": [], "images": [], "specs": [], "datasheets": []},
            "ajax_handling": False,
            "spa_detected": False,
        }

        # Detecta SPA (Single Page Application)
        data_sources = analysis.get("data_sources", {})
        if data_sources.get("ajax_endpoints") or data_sources.get("websockets"):
            strategy["spa_detected"] = True
            strategy["ajax_handling"] = True

        # Gera steps baseado na estrutura
        nav_elements = analysis.get("navigation_elements", [])
        if nav_elements:
            strategy["steps"].append(
                {
                    "step": 1,
                    "action": "analyze_navigation",
                    "description": "Mapear estrutura de navegação",
                    "selectors": [
                        nav["class"] for nav in nav_elements if "class" in nav
                    ],
                }
            )

        # Identifica seletores de produtos
        css_analysis = analysis.get("css_analysis", {})
        for component in css_analysis.get("component_patterns", []):
            if component["type"] in ["card", "gallery"]:
                strategy["selectors"]["products"].extend(component["classes"])

        # Tasks para extração
        strategy["tasks"] = [
            {
                "task": "extract_product_list",
                "method": "css_selector",
                "selectors": strategy["selectors"]["products"][:3],
            },
            {
                "task": "extract_product_images",
                "method": "multi_source",
                "sources": ["img[src]", "img[data-src]", "picture source"],
            },
            {
                "task": "extract_specifications",
                "method": "semantic_search",
                "keywords": ["specifications", "technical", "datasheet"],
            },
        ]

        return strategy


def create_product_discovery_flow(base_url: str) -> NavigationFlow:
    """
    Cria um fluxo padrão de descoberta de produtos

    Args:
        base_url: URL base do site

    Returns:
        NavigationFlow configurado com steps comuns
    """
    scraper = AdvancedScraper()
    flow = scraper.create_navigation_flow("product_discovery", base_url)

    # Step 2: Encontrar seção de produtos
    flow.add_step(
        {
            "action": "find_section",
            "selectors": [
                'nav a:contains("Products")',
                'nav a:contains("Produtos")',
                'a[href*="product"]',
                'a[href*="modelo"]',
            ],
            "description": "Localizar link para seção de produtos",
        }
    )

    # Step 3: Navegar para listagem
    flow.add_step(
        {
            "action": "navigate_to_list",
            "expected_elements": [".product-grid", ".product-list", "article", ".card"],
            "description": "Acessar página de listagem de produtos",
        }
    )

    # Step 4: Extrair URLs de produtos
    flow.add_step(
        {
            "action": "extract_product_urls",
            "selectors": [
                ".product-card a",
                "article a",
                'a[href*="product"]',
                "a.btn-detail",
            ],
            "description": "Extrair URLs de páginas de produto individuais",
        }
    )

    # Task 1: Extrair informações básicas
    flow.add_task(
        {
            "task": "extract_basic_info",
            "fields": ["title", "model", "power", "series"],
            "selectors": {
                "title": ["h1", ".product-title", ".title"],
                "model": [".model", ".sku", '[itemprop="model"]'],
                "power": [".power", ".wattage", 'span:contains("W")'],
            },
        }
    )

    # Task 2: Extrair imagens
    flow.add_task(
        {
            "task": "extract_images",
            "priority": "high",
            "methods": [
                {"type": "direct", "selector": ".product-image img"},
                {"type": "gallery", "selector": ".gallery img, .carousel img"},
                {"type": "lazy", "selector": "img[data-src], img[data-lazy]"},
                {"type": "picture", "selector": "picture source[srcset]"},
            ],
        }
    )

    # Task 3: Extrair datasheet
    flow.add_task(
        {
            "task": "extract_datasheet",
            "priority": "medium",
            "selectors": [
                'a[href$=".pdf"]',
                'a:contains("datasheet")',
                'a:contains("specifications")',
                ".download-link",
            ],
        }
    )

    return flow


if __name__ == "__main__":
    # Exemplo de uso
    print("🔧 Advanced Scraper - Análise de Estrutura de Sites\n")

    scraper = AdvancedScraper()

    # Cria fluxo de descoberta de produtos
    flow = create_product_discovery_flow("https://example.com")

    print(f"📋 Fluxo criado: {flow.name}")
    print(f"   Steps: {len(flow.steps)}")
    print(f"   Tasks: {len(flow.tasks)}")
    print("\n📍 Steps:")
    for step in flow.steps:
        step_num = step.get("step_number", step.get("action"))
        print(f"   {step_num}. {step['description']}")

    print("\n✅ Tasks:")
    for task in flow.tasks:
        print(f"   - {task['task']} (priority: {task.get('priority', 'normal')})")
