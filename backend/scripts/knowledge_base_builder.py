"""
Knowledge Base Builder - Construtor de Base de Conhecimento

Este módulo crawlea sites de fabricantes e constrói uma base de conhecimento
indexada que pode ser usada para busca semântica de produtos.
"""

import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, Set, List, Tuple
from collections import Counter, defaultdict
from config import HTTP_HEADERS, REQUEST_TIMEOUT


class KnowledgeBaseBuilder:
    def __init__(
        self,
        base_url: str,
        manufacturer: str,
        max_depth: int = 3,
        seed_urls: List[str] = None,
    ):
        self.base_url = base_url
        self.manufacturer = manufacturer
        self.max_depth = max_depth
        self.seed_urls = seed_urls or []  # URLs prioritárias para crawling
        self.visited_urls: Set[str] = set()
        self.knowledge_base: Dict[str, Dict] = {}
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

        # Análise de estrutura do site
        self.url_patterns: Counter = Counter()
        self.path_segments: defaultdict = defaultdict(int)
        self.css_selectors: Dict[str, List] = {}
        self.site_structure: Dict[str, List] = defaultdict(list)
        self.product_indicators: List[str] = [
            "product",
            "modelo",
            "model",
            "series",
            "inverter",
            "panel",
            "painel",
            "inversor",
            "solar",
            "module",
            "specification",
            "datasheet",
            "technical",
            "tecnico",
        ]

    def _discover_urls_from_sitemap(self) -> List[str]:
        """Descobre URLs de produtos via sitemap.xml"""
        try:
            from sitemap_parser import SitemapParser

            parser = SitemapParser(self.base_url)
            product_urls = parser.get_product_urls(
                keywords=self.product_indicators, min_priority=0.5
            )
            return product_urls[:50]  # Limita a 50 URLs do sitemap
        except Exception as e:
            print(f"   ⚠️  Erro ao buscar sitemap: {e}")
            return []

    def _is_valid_url(self, url: str) -> bool:
        """Verifica se a URL pertence ao domínio do fabricante"""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == parsed_base.netloc

    def _analyze_url_pattern(self, url: str) -> Dict:
        """Analisa padrões de URL para identificar estrutura do site"""
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        segments = [s for s in path.split("/") if s]

        # Registra segmentos de path
        for i, segment in enumerate(segments):
            self.path_segments[f"depth_{i}"] += 1
            self.site_structure[f"level_{i}"].append(segment)

        # Identifica padrão de URL
        pattern = "/".join(["*" if re.search(r"\d", s) else s for s in segments])
        self.url_patterns[pattern] += 1

        # Verifica indicadores de produto
        is_product_page = any(
            indicator in path.lower() for indicator in self.product_indicators
        )

        return {
            "pattern": pattern,
            "depth": len(segments),
            "segments": segments,
            "is_product_page": is_product_page,
            "has_query": bool(parsed.query),
        }

    def _analyze_html_structure(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analisa estrutura HTML e CSS para entender layout do site"""
        structure = {
            "css_classes": Counter(),
            "css_ids": [],
            "semantic_tags": Counter(),
            "product_containers": [],
            "image_patterns": [],
            "link_patterns": [],
        }

        # Analisa classes CSS usadas
        for tag in soup.find_all(class_=True):
            classes = tag.get("class", [])
            for cls in classes:
                structure["css_classes"][cls] += 1
                # Identifica containers de produtos
                if any(ind in cls.lower() for ind in self.product_indicators):
                    structure["product_containers"].append(
                        {
                            "tag": tag.name,
                            "class": cls,
                            "has_images": bool(tag.find_all("img")),
                            "has_links": bool(tag.find_all("a")),
                        }
                    )

        # Analisa IDs CSS
        for tag in soup.find_all(id=True):
            structure["css_ids"].append(tag.get("id"))

        # Analisa tags semânticas HTML5
        semantic_tags = ["article", "section", "main", "aside", "figure"]
        for tag_name in semantic_tags:
            count = len(soup.find_all(tag_name))
            if count > 0:
                structure["semantic_tags"][tag_name] = count

        # Analisa padrões de imagens
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy")
            if src:
                structure["image_patterns"].append(
                    {
                        "src": src,
                        "alt": img.get("alt", ""),
                        "class": " ".join(img.get("class", [])),
                        "parent": img.parent.name if img.parent else None,
                    }
                )

        # Analisa padrões de links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            structure["link_patterns"].append(
                {
                    "href": href,
                    "text": text,
                    "class": " ".join(link.get("class", [])),
                    "is_product": any(
                        ind in text.lower() for ind in self.product_indicators
                    ),
                }
            )

        return structure

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extrai o texto relevante de uma página"""
        # Remove scripts, styles e outras tags irrelevantes
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extrai o texto
        text = soup.get_text(separator=" ", strip=True)
        # Limpa espaços múltiplos
        text = " ".join(text.split())
        return text

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extrai todos os links válidos de uma página"""
        links = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(current_url, link["href"])
            # Remove fragmentos (#) e queries (?)
            full_url = full_url.split("#")[0].split("?")[0]

            if self._is_valid_url(full_url) and full_url not in self.visited_urls:
                links.append(full_url)

        return links

    def _crawl_page(self, url: str, depth: int = 0):
        """Crawlea uma página e extrai seu conteúdo"""
        if depth > self.max_depth or url in self.visited_urls:
            return

        try:
            print(f"{'  ' * depth}🔍 Crawling: {url} (depth: {depth})")
            self.visited_urls.add(url)

            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Analisa padrão de URL
            url_analysis = self._analyze_url_pattern(url)

            # Analisa estrutura HTML/CSS
            html_structure = self._analyze_html_structure(soup, url)

            # Extrai conteúdo
            text_content = self._extract_text_content(soup)
            title = soup.title.string if soup.title else ""

            # Armazena na base de conhecimento com análises
            self.knowledge_base[url] = {
                "title": title,
                "content": text_content[:5000],  # Limita o tamanho
                "url": url,
                "depth": depth,
                "url_pattern": url_analysis["pattern"],
                "path_segments": url_analysis["segments"],
                "is_product_page": url_analysis["is_product_page"],
                "product_containers": html_structure["product_containers"][:5],
                "image_count": len(html_structure["image_patterns"]),
                "link_count": len(html_structure["link_patterns"]),
                "top_css_classes": dict(html_structure["css_classes"].most_common(10)),
            }

            # Extrai links e continua o crawling
            if depth < self.max_depth:
                links = self._extract_links(soup, url)
                for link in links[:10]:  # Limita para não sobrecarregar
                    time.sleep(0.5)  # Rate limiting
                    self._crawl_page(link, depth + 1)

        except Exception as e:
            print(f"❌ Erro ao crawlear {url}: {e}")

    @staticmethod
    def load_from_file(kb_file: str) -> Dict:
        """Carrega uma base de conhecimento de um arquivo JSON"""
        with open(kb_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def build(self) -> Dict:
        """Constrói a base de conhecimento"""
        print(f"\n🚀 Iniciando crawling de {self.manufacturer}")
        print(f"   URL Base: {self.base_url}")
        print(f"   Profundidade Máxima: {self.max_depth}\n")

        self._crawl_page(self.base_url)

        print(f"\n✅ Crawling concluído!")
        print(f"   Total de páginas indexadas: {len(self.knowledge_base)}")

        # Gera relatório de estrutura do site
        self._generate_site_analysis_report()

        return self.knowledge_base

    def _generate_site_analysis_report(self):
        """Gera relatório de análise da estrutura do site"""
        print(f"\n📊 ANÁLISE DA ESTRUTURA DO SITE")
        print("=" * 70)

        # Padrões de URL mais comuns
        print(f"\n🔗 Top 5 Padrões de URL:")
        for pattern, count in self.url_patterns.most_common(5):
            print(f"   {pattern}: {count} ocorrências")

        # Estrutura de níveis
        print(f"\n📁 Estrutura de Níveis:")
        for level in sorted(self.site_structure.keys()):
            segments = self.site_structure[level]
            unique = set(segments)
            print(f"   {level}: {len(unique)} segmentos únicos")
            if len(unique) <= 10:
                print(f"      → {', '.join(sorted(unique)[:10])}")

        # Páginas de produtos identificadas
        product_pages = [
            url
            for url, data in self.knowledge_base.items()
            if data.get("is_product_page", False)
        ]
        print(f"\n🎯 Páginas de Produto Identificadas: {len(product_pages)}")
        for url in product_pages[:5]:
            print(f"   - {url}")

        # Páginas com mais imagens
        pages_with_images = sorted(
            [
                (url, data.get("image_count", 0))
                for url, data in self.knowledge_base.items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        print(f"\n🖼️  Top 5 Páginas com Mais Imagens:")
        for url, count in pages_with_images:
            print(f"   {count} imagens: {url}")

    def save(self, output_file: str):
        """Salva a base de conhecimento em arquivo JSON

        Args:
            output_file: Caminho completo do arquivo (ex: 'output/kb/jinko_kb.json')
        """
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)

        print(f"💾 Base de conhecimento salva em: {output_file}")
        return output_file

    @staticmethod
    def load(manufacturer: str, kb_dir: str = "output/knowledge_bases") -> Dict:
        """Carrega uma base de conhecimento existente"""
        kb_path = os.path.join(
            kb_dir, f"{manufacturer.lower().replace(' ', '_')}_kb.json"
        )

        if not os.path.exists(kb_path):
            return None

        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)


if __name__ == "__main__":
    # Exemplo de uso
    builder = KnowledgeBaseBuilder(
        base_url="https://www.deyeinverter.com/products/",
        manufacturer="Deye",
        max_depth=2,
    )

    kb = builder.build()
    builder.save()

    print(f"\n📊 Exemplo de entrada na base:")
    for url, data in list(kb.items())[:2]:
        print(f"\nURL: {url}")
        print(f"Título: {data['title']}")
        print(f"Conteúdo (preview): {data['content'][:200]}...")
