"""
Semantic Web Scraper - Navegação inteligente via LLMs
------------------------------------------------------
Usa modelos de linguagem para entender a estrutura de sites de fabricantes
e descobrir URLs de produtos através de análise semântica.

Inspirado no Computer Use Agent Handbook para automação de web scraping.
"""

import os
import re
import json
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
from agent_manager import AgentManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PageAnalysis:
    """Análise semântica de uma página web"""

    url: str
    title: str
    main_content: str
    links: List[Dict[str, str]]  # {"url": str, "text": str, "context": str}
    is_product_page: bool
    product_info: Optional[Dict[str, Any]]
    semantic_score: float  # 0-1: relevância para busca de produtos


@dataclass
class ProductDiscovery:
    """Resultado da descoberta de produto"""

    sku: str
    manufacturer: str
    product_urls: List[str]  # URLs descobertas (datasheet, imagem, página)
    confidence_score: float
    discovery_method: str
    metadata: Dict[str, Any]


class SemanticWebScraper:
    """
    Scraper inteligente que usa LLMs para navegar sites e encontrar produtos.
    """

    def __init__(self, agent_manager: AgentManager):
        self.agent = agent_manager
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.visited_urls = set()
        self.discovered_products = {}

    def analyze_page_semantically(self, url: str) -> Optional[PageAnalysis]:
        """
        Analisa página usando LLM para extrair informações semânticas.
        """
        try:
            # Fetch HTML
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts e styles
            for script in soup(["script", "style", "noscript"]):
                script.decompose()

            # Extrai texto principal
            title = soup.find("title").get_text() if soup.find("title") else ""
            main_text = soup.get_text(separator="\n", strip=True)[
                :3000
            ]  # Limita contexto

            # Extrai links
            links = []
            for link in soup.find_all("a", href=True):
                link_url = urljoin(url, link["href"])
                link_text = link.get_text(strip=True)
                # Contexto ao redor do link
                parent_text = (
                    link.parent.get_text(strip=True)[:200] if link.parent else ""
                )

                links.append(
                    {"url": link_url, "text": link_text, "context": parent_text}
                )

            # Usa LLM para análise semântica
            analysis_prompt = f"""
Analise esta página web e responda em JSON:

URL: {url}
Título: {title}
Conteúdo principal (primeiras 3000 caracteres):
{main_text}

Responda:
1. Esta é uma página de produto? (true/false)
2. Se for produto, extraia: nome, modelo, especificações técnicas
3. Score de relevância para produtos solares (0.0-1.0)
4. Identifique links relevantes para: datasheet PDF, imagens de produto, especificações

JSON:
{{
    "is_product_page": boolean,
    "product_info": {{"name": str, "model": str, "specs": dict}} ou null,
    "relevance_score": float,
    "relevant_links": [
        {{"url": str, "type": "datasheet|image|specs", "confidence": float}}
    ]
}}
"""

            agent_response = self.agent.get_agent().query(analysis_prompt)
            analysis_json = self._extract_json_from_response(agent_response)

            if not analysis_json:
                logger.warning(f"Falha ao extrair JSON da análise de {url}")
                return None

            return PageAnalysis(
                url=url,
                title=title,
                main_content=main_text[:500],
                links=links,
                is_product_page=analysis_json.get("is_product_page", False),
                product_info=analysis_json.get("product_info"),
                semantic_score=analysis_json.get("relevance_score", 0.0),
            )

        except Exception as e:
            logger.error(f"Erro ao analisar {url}: {e}")
            return None

    def discover_product_urls(
        self, manufacturer_domain: str, product_query: str, max_depth: int = 3
    ) -> List[ProductDiscovery]:
        """
        Descobre URLs de produtos através de navegação semântica.

        Args:
            manufacturer_domain: Domínio do fabricante (ex: "solisinverters.com")
            product_query: Consulta de produto (ex: "Solis S5 6kW inverter")
            max_depth: Profundidade máxima de navegação

        Returns:
            Lista de descobertas de produtos
        """
        logger.info(
            f"Iniciando descoberta semântica: {manufacturer_domain} - {product_query}"
        )

        # 1. Tenta encontrar sitemap
        sitemap_urls = self._discover_sitemap(manufacturer_domain)

        # 2. Navegação guiada por LLM
        start_url = f"https://{manufacturer_domain}"
        to_visit = [(start_url, 0)]  # (url, depth)
        discovered = []

        while to_visit and len(discovered) < 10:  # Limite de descobertas
            current_url, depth = to_visit.pop(0)

            if current_url in self.visited_urls or depth > max_depth:
                continue

            self.visited_urls.add(current_url)
            logger.info(f"Analisando [{depth}]: {current_url}")

            # Analisa página
            analysis = self.analyze_page_semantically(current_url)
            if not analysis:
                continue

            # Se encontrou página de produto
            if analysis.is_product_page and analysis.semantic_score > 0.6:
                discovery = ProductDiscovery(
                    sku="",  # Será preenchido depois
                    manufacturer=manufacturer_domain.split(".")[0].upper(),
                    product_urls=[current_url],
                    confidence_score=analysis.semantic_score,
                    discovery_method="semantic_navigation",
                    metadata={"analysis": asdict(analysis)},
                )
                discovered.append(discovery)

            # Decide quais links visitar usando LLM
            if depth < max_depth:
                next_links = self._select_promising_links(
                    analysis.links, product_query, max_links=5
                )

                for link_url in next_links:
                    to_visit.append((link_url, depth + 1))

            time.sleep(1)  # Rate limiting

        logger.info(f"Descoberta concluída: {len(discovered)} produtos encontrados")
        return discovered

    def _discover_sitemap(self, domain: str) -> List[str]:
        """Tenta descobrir e parsear sitemap.xml"""
        sitemap_candidates = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/robots.txt",
        ]

        urls = []
        for candidate in sitemap_candidates:
            try:
                response = self.session.get(candidate, timeout=5)
                if response.status_code == 200:
                    if candidate.endswith("robots.txt"):
                        # Extrai sitemap do robots.txt
                        for line in response.text.split("\n"):
                            if line.lower().startswith("sitemap:"):
                                sitemap_url = line.split(":", 1)[1].strip()
                                urls.extend(self._parse_sitemap(sitemap_url))
                    else:
                        # Parse XML sitemap
                        urls.extend(self._parse_sitemap(candidate))
            except:
                continue

        return urls

    def _parse_sitemap(self, url: str) -> List[str]:
        """Parse sitemap XML"""
        try:
            response = self.session.get(url, timeout=5)
            soup = BeautifulSoup(response.content, "xml")
            return [loc.text for loc in soup.find_all("loc")]
        except:
            return []

    def _select_promising_links(
        self, links: List[Dict[str, str]], query: str, max_links: int = 5
    ) -> List[str]:
        """
        Usa LLM para selecionar links mais promissores.
        """
        if not links:
            return []

        # Limita para não sobrecarregar o prompt
        links_sample = links[:20]

        prompt = f"""
Você está navegando um site de fabricante de equipamentos solares.
Objetivo: Encontrar informações sobre "{query}"

Links disponíveis:
{json.dumps(links_sample, indent=2, ensure_ascii=False)}

Selecione os {max_links} links MAIS PROMISSORES para encontrar:
- Páginas de produtos
- Datasheets PDF
- Especificações técnicas
- Imagens de produtos

Responda apenas com JSON:
{{
    "selected_urls": ["url1", "url2", ...]
}}
"""

        try:
            response = self.agent.get_agent().query(prompt)
            result = self._extract_json_from_response(response)
            return result.get("selected_urls", [])[:max_links]
        except:
            # Fallback: usa heurística simples
            return self._heuristic_link_selection(links, query, max_links)

    def _heuristic_link_selection(
        self, links: List[Dict[str, str]], query: str, max_links: int
    ) -> List[str]:
        """Seleção heurística de links (fallback)"""
        keywords = query.lower().split()
        scored_links = []

        for link in links:
            url = link["url"].lower()
            text = link["text"].lower()
            context = link["context"].lower()

            # Score baseado em palavras-chave
            score = 0
            for keyword in keywords:
                if keyword in url:
                    score += 3
                if keyword in text:
                    score += 2
                if keyword in context:
                    score += 1

            # Bonus para padrões conhecidos
            if any(
                pattern in url
                for pattern in ["/product", "/datasheet", "/download", "/specs"]
            ):
                score += 5

            if ".pdf" in url:
                score += 10

            scored_links.append((score, link["url"]))

        scored_links.sort(reverse=True)
        return [url for score, url in scored_links[:max_links] if score > 0]

    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extrai JSON de resposta de LLM"""
        try:
            # Tenta encontrar bloco JSON
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Tenta parsear diretamente
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            return None
        except json.JSONDecodeError:
            return None

    def extract_images_from_page(self, url: str) -> List[str]:
        """
        Extrai URLs de imagens de alta qualidade de uma página de produto.
        """
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            images = []
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src:
                    img_url = urljoin(url, src)
                    # Filtra imagens pequenas (provavelmente não são packshots)
                    if not any(
                        skip in img_url.lower()
                        for skip in ["icon", "logo", "banner", "thumb"]
                    ):
                        images.append(img_url)

            return images
        except Exception as e:
            logger.error(f"Erro ao extrair imagens de {url}: {e}")
            return []


# Exemplo de uso
if __name__ == "__main__":
    from config import GEMINI_API_KEYS, OPENAI_API_KEY, DOCKER_MODELS

    # Inicializa agent manager
    agent_mgr = AgentManager(
        gemini_keys=GEMINI_API_KEYS,
        openai_key=OPENAI_API_KEY,
        docker_models=DOCKER_MODELS,
    )

    # Cria scraper
    scraper = SemanticWebScraper(agent_mgr)

    # Teste: descobre produtos Solis
    discoveries = scraper.discover_product_urls(
        manufacturer_domain="solisinverters.com",
        product_query="Solis S5 hybrid inverter 6kW",
        max_depth=2,
    )

    print(f"\n✅ Descobertas: {len(discoveries)}")
    for disc in discoveries:
        print(
            f"  - {disc.manufacturer}: {disc.product_urls[0]} (score: {disc.confidence_score:.2f})"
        )
