"""
Semantic Scraper - Extração Inteligente de Imagens

Este módulo usa LLMs para analisar páginas HTML e identificar
inteligentemente as URLs de imagens de produtos (packshots) e datasheets.
Inclui análise avançada de estrutura HTML/CSS e path patterns.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin

from config import HTTP_HEADERS, REQUEST_TIMEOUT
from agent_manager import AgentManager
from advanced_scraper import AdvancedScraper
from playwright_scraper import PlaywrightScraper


class SemanticScraper:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)
        self.advanced_scraper = AdvancedScraper()
        self.playwright_scraper = PlaywrightScraper()  # 🆕 Camada 2

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """Busca o conteúdo HTML de uma página"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Erro ao buscar página {url}: {e}")
            return None

    def _extract_image_candidates(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict]:
        """Extrai todos os candidatos a imagem de uma página"""
        candidates = []

        # 1. Meta tags (og:image, twitter:image)
        for meta in soup.find_all("meta", property=["og:image", "twitter:image"]):
            if meta.get("content"):
                candidates.append(
                    {
                        "url": urljoin(base_url, meta["content"]),
                        "type": "meta_tag",
                        "source": meta.get("property", "meta"),
                    }
                )

        # 2. Imagens com classes/ids sugestivos
        image_keywords = [
            "product",
            "packshot",
            "main",
            "hero",
            "feature",
            "module",
            "panel",
            "inverter",
            "gallery",
        ]

        for img in soup.find_all("img"):
            img_src = img.get("src") or img.get("data-src")
            if not img_src:
                continue

            img_class = " ".join(img.get("class", [])).lower()
            img_id = img.get("id", "").lower()
            img_alt = img.get("alt", "").lower()

            # Verifica se contém palavras-chave
            relevance = 0
            for keyword in image_keywords:
                if keyword in img_class or keyword in img_id or keyword in img_alt:
                    relevance += 1

            if relevance > 0 or "datasheet" in img_src.lower():
                candidates.append(
                    {
                        "url": urljoin(base_url, img_src),
                        "type": "img_tag",
                        "relevance": relevance,
                        "alt": img_alt,
                        "class": img_class,
                    }
                )

        # 3. Links para PDFs (datasheets)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith(".pdf"):
                link_text = link.get_text(strip=True).lower()
                if "datasheet" in link_text or "manual" in link_text:
                    candidates.append(
                        {
                            "url": urljoin(base_url, href),
                            "type": "pdf_link",
                            "text": link_text,
                        }
                    )

        return candidates

    def _use_llm_to_select_best(
        self, candidates: List[Dict], product_name: str
    ) -> Optional[Dict]:
        """Usa LLM para selecionar a melhor imagem dos candidatos"""
        if not candidates:
            return None

        agent = self.agent_manager.get_agent()
        if not agent:
            # Fallback: usa heurística simples
            return self._heuristic_selection(candidates)

        # Prepara prompt para o LLM
        prompt = f"""Você é um assistente especializado em identificar imagens de produtos solares.

Produto: {product_name}

Candidatos de imagem encontrados:
"""
        for i, cand in enumerate(candidates, 1):
            prompt += f"\n{i}. URL: {cand['url']}"
            prompt += f"\n   Tipo: {cand['type']}"
            if "relevance" in cand:
                prompt += f"\n   Relevância: {cand['relevance']}"
            if "alt" in cand:
                prompt += f"\n   Alt text: {cand['alt']}"

        prompt += """\n\nQual é o MELHOR candidato para a imagem principal (packshot) do produto?
Considere:
- Imagens de produto geralmente têm "product", "packshot", "main" no nome/classe
- Meta tags (og:image) são frequentemente a melhor opção
- PDFs de datasheet são aceitáveis se não houver imagem direta

Responda APENAS com o número do candidato (1, 2, 3, etc.)"""

        # TODO: Implementar chamada real ao LLM via agent_manager
        # Por enquanto, usa fallback heurístico
        return self._heuristic_selection(candidates)

    def _heuristic_selection(self, candidates: List[Dict]) -> Optional[Dict]:
        """Seleção heurística quando LLM não está disponível"""
        # Prioriza meta tags
        meta_candidates = [c for c in candidates if c["type"] == "meta_tag"]
        if meta_candidates:
            return meta_candidates[0]

        # Prioriza imagens com alta relevância
        img_candidates = [c for c in candidates if c["type"] == "img_tag"]
        if img_candidates:
            img_candidates.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            return img_candidates[0]

        # Fallback: PDFs
        pdf_candidates = [c for c in candidates if c["type"] == "pdf_link"]
        if pdf_candidates:
            return pdf_candidates[0]

        return None

    def extract_product_images(
        self, product_url: str, product_name: str, max_images: int = 5
    ) -> List[Dict]:
        """
        Extrai URLs de imagens de uma página de produto.

        Args:
            product_url: URL da página do produto
            product_name: Nome do produto (para contexto do LLM)
            max_images: Número máximo de imagens a retornar

        Returns:
            Lista de dicts com URLs e metadados das imagens
        """
        print(f"\n🔍 Analisando página: {product_url}")

        # Busca conteúdo
        html_content = self._fetch_page_content(product_url)
        if not html_content:
            return []

        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Análise avançada da estrutura da página
        print("📊 Analisando estrutura HTML/CSS...")
        page_analysis = self.advanced_scraper.analyze_page_structure(
            html_content, product_url
        )

        # Exibe resumo da análise
        css_info = page_analysis.get("css_analysis", {})
        if css_info.get("framework_detected"):
            print(f"   Framework CSS: {css_info['framework_detected']}")

        component_patterns = css_info.get("component_patterns", [])
        if component_patterns:
            print(f"   Componentes: {[c['type'] for c in component_patterns]}")

        # Gera estratégia de scraping
        strategy = self.advanced_scraper.generate_scraping_strategy(page_analysis)

        if strategy.get("spa_detected"):
            print("   ⚡ SPA/AJAX detectado")

        print(f"   📋 {len(strategy['tasks'])} tasks de extração geradas")

        # 🆕 CAMADA 1: Extração rápida com requests
        candidates = self._extract_image_candidates(soup, product_url)
        print(f"   Encontrados {len(candidates)} candidatos de imagem")

        # 🆕 CAMADA 2: Se SPA ou sem resultados, usa Playwright
        if strategy.get("spa_detected") or len(candidates) == 0:
            print("   🎭 Ativando Playwright (Camada 2)...")
            try:
                playwright_result = self.playwright_scraper.extract_with_browser(
                    product_url
                )

                # Parse HTML renderizado
                rendered_soup = BeautifulSoup(playwright_result["html"], "html.parser")
                playwright_candidates = self._extract_image_candidates(
                    rendered_soup, product_url
                )

                # Adiciona imagens descobertas via API interception
                for img_url in playwright_result["images"]:
                    playwright_candidates.append(
                        {
                            "url": img_url,
                            "type": "playwright_intercepted",
                            "relevance": 3,  # Alta prioridade
                        }
                    )

                candidates.extend(playwright_candidates)
                print(
                    f"   ✅ Playwright adicionou {len(playwright_candidates)} candidatos"
                )
            except Exception as e:
                print(f"   ⚠️ Erro no Playwright: {e}")
                print("   Continuando com candidatos da Camada 1...")

        if not candidates:
            return []

        # Usa LLM para selecionar o melhor
        best = self._use_llm_to_select_best(candidates, product_name)

        if best:
            print(f"   ✅ Melhor candidato: {best['url']} (tipo: {best['type']})")

            # Retorna o melhor + outros relevantes
            results = [best]
            for cand in candidates:
                if cand != best and len(results) < max_images:
                    results.append(cand)

            return results

        print("   ⚠️ Nenhum candidato adequado encontrado")
        return []


if __name__ == "__main__":
    scraper = SemanticScraper()

    # Teste com uma URL real (exemplo)
    test_url = "https://www.deyeinverter.com/product/sun-8k-sg04lp3-eu/"
    product_name = "Deye SUN-8K-SG04LP3-EU"

    images = scraper.extract_product_images(test_url, product_name)

    print(f"\n📸 Imagens extraídas para {product_name}:")
    for i, img in enumerate(images, 1):
        print(f"{i}. {img['url']} (tipo: {img['type']})")
