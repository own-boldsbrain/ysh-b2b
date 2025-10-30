"""
Sitemap Parser - Parser de Sitemap XML

Este módulo extrai URLs de sitemaps XML para priorizar crawling de páginas importantes.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from config import HTTP_HEADERS, REQUEST_TIMEOUT


class SitemapParser:
    """Parser para extrair URLs de sitemap.xml"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def _fetch_robots_txt(self) -> Optional[str]:
        """Busca robots.txt para encontrar sitemap"""
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = self.session.get(robots_url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"⚠️  Erro ao buscar robots.txt: {e}")
        return None

    def _extract_sitemap_urls_from_robots(self, robots_content: str) -> List[str]:
        """Extrai URLs de sitemap do robots.txt"""
        sitemap_urls = []
        for line in robots_content.split("\n"):
            if line.lower().startswith("sitemap:"):
                url = line.split(":", 1)[1].strip()
                sitemap_urls.append(url)
        return sitemap_urls

    def _parse_sitemap_xml(self, sitemap_url: str) -> List[Dict]:
        """Parseia um arquivo sitemap.xml e retorna lista de URLs"""
        urls = []
        try:
            response = self.session.get(sitemap_url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return urls

            # Parse XML
            root = ET.fromstring(response.content)

            # Define namespaces comuns
            namespaces = {
                "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                "": "http://www.sitemaps.org/schemas/sitemap/0.9",
            }

            # Verifica se é um sitemap index (contém outros sitemaps)
            sitemap_elements = root.findall(
                ".//sm:sitemap", namespaces
            ) or root.findall(".//sitemap", namespaces)

            if sitemap_elements:
                # É um sitemap index, processar cada sitemap filho
                for sitemap in sitemap_elements:
                    loc = sitemap.find("sm:loc", namespaces) or sitemap.find(
                        "loc", namespaces
                    )
                    if loc is not None and loc.text:
                        child_urls = self._parse_sitemap_xml(loc.text)
                        urls.extend(child_urls)
            else:
                # É um sitemap normal, extrair URLs
                url_elements = root.findall(".//sm:url", namespaces) or root.findall(
                    ".//url", namespaces
                )

                for url_elem in url_elements:
                    loc = url_elem.find("sm:loc", namespaces) or url_elem.find(
                        "loc", namespaces
                    )
                    priority = url_elem.find(
                        "sm:priority", namespaces
                    ) or url_elem.find("priority", namespaces)

                    if loc is not None and loc.text:
                        urls.append(
                            {
                                "url": loc.text,
                                "priority": (
                                    float(priority.text)
                                    if priority is not None and priority.text
                                    else 0.5
                                ),
                            }
                        )

        except Exception as e:
            print(f"⚠️  Erro ao parsear sitemap {sitemap_url}: {e}")

        return urls

    def get_product_urls(
        self, keywords: List[str] = None, min_priority: float = 0.0
    ) -> List[str]:
        """
        Obtém URLs de produtos do sitemap

        Args:
            keywords: Palavras-chave para filtrar URLs (ex: ['product', 'modelo'])
            min_priority: Prioridade mínima da URL (0.0 a 1.0)

        Returns:
            Lista de URLs filtradas
        """
        if keywords is None:
            keywords = [
                "product",
                "modelo",
                "model",
                "series",
                "panel",
                "inverter",
                "painel",
                "inversor",
                "module",
            ]

        all_urls = []

        # Tenta descobrir sitemap via robots.txt
        print(f"🔍 Buscando sitemap via robots.txt...")
        robots_content = self._fetch_robots_txt()

        sitemap_urls = []
        if robots_content:
            sitemap_urls = self._extract_sitemap_urls_from_robots(robots_content)
            print(f"   Encontrados {len(sitemap_urls)} sitemaps no robots.txt")

        # Se não encontrou no robots.txt, tenta URLs padrão
        if not sitemap_urls:
            print(f"   Tentando URLs padrão de sitemap...")
            sitemap_urls = [
                urljoin(self.base_url, "/sitemap.xml"),
                urljoin(self.base_url, "/sitemap_index.xml"),
                urljoin(self.base_url, "/sitemap-index.xml"),
            ]

        # Parseia cada sitemap
        for sitemap_url in sitemap_urls:
            print(f"   Parseando: {sitemap_url}")
            urls = self._parse_sitemap_xml(sitemap_url)
            all_urls.extend(urls)

        if not all_urls:
            print(f"   ⚠️  Nenhuma URL encontrada em sitemaps")
            return []

        print(f"   ✅ Total de URLs no sitemap: {len(all_urls)}")

        # Filtra por keywords e priority
        filtered_urls = []
        for url_data in all_urls:
            url = url_data["url"]
            priority = url_data["priority"]

            # Verifica prioridade
            if priority < min_priority:
                continue

            # Verifica keywords
            url_lower = url.lower()
            if any(keyword in url_lower for keyword in keywords):
                filtered_urls.append(url)

        print(f"   ✅ URLs de produtos filtradas: {len(filtered_urls)}")

        return filtered_urls


if __name__ == "__main__":
    # Teste
    parser = SitemapParser("https://www.jinkosolar.com")
    product_urls = parser.get_product_urls()

    print(f"\n📋 URLs de produtos encontradas ({len(product_urls)}):")
    for url in product_urls[:10]:
        print(f"   - {url}")
