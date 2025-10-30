"""
Playwright Scraper - Extração com Browser Automation

Este módulo usa Playwright para renderizar JavaScript e extrair dados de SPAs.
Camada 2 da arquitetura de extração adaptativa.
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class PlaywrightScraper:
    """Scraper com browser automation para sites dinâmicos"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.playwright_available = self._check_playwright()

    def _check_playwright(self) -> bool:
        """Verifica se Playwright está instalado"""
        try:
            from playwright.sync_api import sync_playwright

            return True
        except ImportError:
            print("⚠️  Playwright não instalado")
            print("   Instale com: pip install playwright")
            print("   E depois: playwright install chromium")
            return False

    def _init_browser(self):
        """Inicializa o browser Playwright"""
        if not self.playwright_available:
            return False

        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True, args=["--disable-blink-features=AutomationControlled"]
            )
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao inicializar Playwright: {e}")
            return False

    def _close_browser(self):
        """Fecha o browser"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, "playwright"):
                self.playwright.stop()
        except Exception as e:
            print(f"⚠️  Erro ao fechar browser: {e}")

    def fetch_rendered_html(
        self, url: str, wait_for: str = None, timeout: int = 30000
    ) -> Optional[str]:
        """
        Busca HTML renderizado após execução de JavaScript

        Args:
            url: URL para visitar
            wait_for: Seletor CSS para aguardar antes de extrair HTML
            timeout: Timeout em milissegundos

        Returns:
            HTML renderizado ou None
        """
        if not self.playwright_available:
            return None

        if not self.browser:
            if not self._init_browser():
                return None

        try:
            print(f"\n🌐 Playwright: Renderizando {url}...")

            page = self.context.new_page()

            # Navega para a página
            page.goto(url, wait_until="networkidle", timeout=timeout)

            # Aguarda seletor específico se fornecido
            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=10000)
                    print(f"   ✅ Elemento '{wait_for}' carregado")
                except:
                    print(f"   ⚠️  Timeout aguardando '{wait_for}'")

            # Scroll para carregar lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # Aguarda 2s para lazy loading

            # Extrai HTML renderizado
            html = page.content()
            page.close()

            print(f"   ✅ HTML renderizado ({len(html)} bytes)")
            return html

        except Exception as e:
            print(f"   ❌ Erro ao renderizar: {e}")
            return None

    def intercept_api_calls(self, url: str, timeout: int = 30000) -> Dict:
        """
        Intercepta chamadas de API e extrai dados JSON

        Args:
            url: URL para visitar
            timeout: Timeout em milissegundos

        Returns:
            Dict com APIs interceptadas e seus dados
        """
        if not self.playwright_available or not self.browser:
            if not self._init_browser():
                return {}

        api_data = {"endpoints": [], "json_responses": []}

        try:
            print(f"\n🕵️  Interceptando APIs em: {url}...")

            page = self.context.new_page()

            # Handler para interceptar respostas
            def handle_response(response):
                try:
                    # Filtra apenas respostas relevantes
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")

                        if "application/json" in content_type:
                            api_data["endpoints"].append(response.url)

                            # Tenta extrair JSON
                            try:
                                json_data = response.json()
                                api_data["json_responses"].append(
                                    {"url": response.url, "data": json_data}
                                )
                                print(f"   📦 JSON capturado: {response.url}")
                            except:
                                pass
                except:
                    pass

            page.on("response", handle_response)

            # Navega e aguarda requisições
            page.goto(url, wait_until="networkidle", timeout=timeout)
            page.wait_for_timeout(3000)  # Aguarda requisições assíncronas

            page.close()

            print(f"   ✅ {len(api_data['json_responses'])} APIs JSON interceptadas")
            return api_data

        except Exception as e:
            print(f"   ❌ Erro ao interceptar APIs: {e}")
            return api_data

    def extract_with_browser(self, url: str, extract_images: bool = True) -> Dict:
        """
        Extração completa usando browser automation

        Args:
            url: URL para extrair
            extract_images: Se deve extrair URLs de imagens

        Returns:
            Dict com dados extraídos
        """
        result = {"html": None, "images": [], "api_data": None}

        # 1. Intercepta APIs
        api_data = self.intercept_api_calls(url)
        result["api_data"] = api_data

        # 2. Extrai HTML renderizado
        html = self.fetch_rendered_html(url)
        result["html"] = html

        # 3. Extrai imagens do HTML renderizado
        if html and extract_images:
            soup = BeautifulSoup(html, "html.parser")
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy")
                if src:
                    result["images"].append(
                        {
                            "src": src,
                            "alt": img.get("alt", ""),
                            "class": " ".join(img.get("class", [])),
                        }
                    )

            print(
                f"   ✅ {len(result['images'])} imagens extraídas do HTML renderizado"
            )

        return result

    def __del__(self):
        """Cleanup ao destruir objeto"""
        self._close_browser()


if __name__ == "__main__":
    # Teste
    scraper = PlaywrightScraper()

    if scraper.playwright_available:
        # Teste 1: HTML renderizado
        html = scraper.fetch_rendered_html(
            "https://www.jinkosolar.com/en/site/tigerneo"
        )

        if html:
            print(f"\n✅ HTML renderizado com sucesso")
            print(f"   Tamanho: {len(html)} bytes")

        # Teste 2: Interceptação de APIs
        api_data = scraper.intercept_api_calls(
            "https://www.jinkosolar.com/en/site/tigerneo"
        )

        print(f"\n📊 APIs interceptadas: {len(api_data['json_responses'])}")

        scraper._close_browser()
    else:
        print("\n❌ Playwright não disponível")
        print("   Instale com: pip install playwright && playwright install chromium")
