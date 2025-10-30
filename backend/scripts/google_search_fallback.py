"""
Google Search Fallback - Busca no Google como fallback

Este módulo implementa busca no Google como fallback quando o RAG interno
retorna resultados com score baixo.
"""

import requests
from typing import Optional, List, Dict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from config import HTTP_HEADERS, REQUEST_TIMEOUT


class GoogleSearchFallback:
    """Busca no Google como fallback para RAG de baixa confiança"""

    def __init__(
        self, use_official_api: bool = False, api_key: str = None, cx: str = None
    ):
        """
        Inicializa o fallback do Google

        Args:
            use_official_api: Se True, usa Google Custom Search API oficial
            api_key: API key do Google (necessária se use_official_api=True)
            cx: Custom Search Engine ID (necessário se use_official_api=True)
        """
        self.use_official_api = use_official_api
        self.api_key = api_key
        self.cx = cx
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def _search_via_scraping(self, query: str, site: str = None) -> List[str]:
        """
        Busca via scraping do Google (método gratuito mas menos confiável)

        Args:
            query: Query de busca
            site: Limitar busca a um site específico (ex: jinkosolar.com)

        Returns:
            Lista de URLs encontradas
        """
        # Constrói a query
        if site:
            full_query = f"site:{site} {query}"
        else:
            full_query = query

        encoded_query = quote_plus(full_query)
        search_url = f"https://www.google.com/search?q={encoded_query}"

        try:
            # Usa headers específicos para evitar bloqueio
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            response = self.session.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extrai URLs dos resultados
            urls = []
            for result in soup.select("div.g"):
                link = result.select_one("a")
                if link and link.get("href"):
                    href = link["href"]
                    # Remove Google redirect
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]

                    # Valida URL
                    if href.startswith("http") and "google.com" not in href:
                        urls.append(href)

            return urls[:5]  # Retorna top 5

        except Exception as e:
            print(f"   ⚠️  Erro ao buscar no Google (scraping): {e}")
            return []

    def _search_via_api(self, query: str, site: str = None) -> List[Dict]:
        """
        Busca via Google Custom Search API oficial (método pago mas confiável)

        Args:
            query: Query de busca
            site: Limitar busca a um site específico

        Returns:
            Lista de dicts com URLs e metadados
        """
        if not self.api_key or not self.cx:
            print("   ⚠️  Google API key/cx não configurados")
            return []

        # Constrói a query
        if site:
            full_query = f"site:{site} {query}"
        else:
            full_query = query

        api_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": full_query,
            "num": 5,  # Top 5 resultados
        }

        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                results.append(
                    {
                        "url": item["link"],
                        "title": item["title"],
                        "snippet": item.get("snippet", ""),
                    }
                )

            return results

        except Exception as e:
            print(f"   ⚠️  Erro ao buscar no Google (API): {e}")
            return []

    def search(self, query: str, site: str = None) -> Optional[str]:
        """
        Busca no Google e retorna a melhor URL

        Args:
            query: Query de busca
            site: Limitar busca a um site específico

        Returns:
            URL do primeiro resultado ou None
        """
        print(f"\n🔍 Google Search Fallback:")
        print(f"   Query: {query}")
        if site:
            print(f"   Site: {site}")

        if self.use_official_api:
            results = self._search_via_api(query, site)
            if results:
                best_url = results[0]["url"]
                print(f"   ✅ Encontrado via API: {best_url}")
                return best_url
        else:
            urls = self._search_via_scraping(query, site)
            if urls:
                best_url = urls[0]
                print(f"   ✅ Encontrado via scraping: {best_url}")
                return best_url

        print(f"   ❌ Nenhum resultado encontrado")
        return None

    def search_datasheet(
        self, manufacturer: str, model: str, site: str = None
    ) -> Optional[str]:
        """
        Busca especificamente por datasheet PDF

        Args:
            manufacturer: Nome do fabricante
            model: Modelo do produto
            site: Site para limitar busca

        Returns:
            URL do datasheet PDF ou None
        """
        # Tenta com filetype:pdf
        query = f"{manufacturer} {model} datasheet filetype:pdf"

        print(f"\n📄 Buscando datasheet PDF...")
        print(f"   Query: {query}")

        if self.use_official_api:
            results = self._search_via_api(query, site)
            # Filtra apenas PDFs
            pdf_results = [r for r in results if r["url"].lower().endswith(".pdf")]
            if pdf_results:
                url = pdf_results[0]["url"]
                print(f"   ✅ PDF encontrado: {url}")
                return url
        else:
            urls = self._search_via_scraping(query, site)
            # Filtra apenas PDFs
            pdf_urls = [u for u in urls if u.lower().endswith(".pdf")]
            if pdf_urls:
                url = pdf_urls[0]
                print(f"   ✅ PDF encontrado: {url}")
                return url

        print(f"   ❌ Datasheet PDF não encontrado")
        return None


if __name__ == "__main__":
    # Teste
    fallback = GoogleSearchFallback(use_official_api=False)

    # Teste 1: Busca geral
    url = fallback.search(query="Tiger Neo 585W specifications", site="jinkosolar.com")

    # Teste 2: Busca de datasheet
    pdf_url = fallback.search_datasheet(
        manufacturer="Jinko", model="JKM585N-72HL4-V", site="jinkosolar.com"
    )
