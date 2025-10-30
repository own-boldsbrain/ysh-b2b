"""
AI-Guided Web Scraper for YSH Solar Product Images
Uses Gemini/OpenAI to intelligently navigate manufacturer websites
"""

import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import cv2
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIGuidedScraper:
    """
    Scraper inteligente guiado por LLMs (Gemini/GPT-4)
    Implementa as heurísticas definidas no mega-prompt
    """

    def __init__(
        self,
        manufacturer_name: str,
        base_url: str,
        output_dir: str,
        mega_prompt_path: str = "/app/docs/ai-ml/mega-prompt-image-capture.md",
    ):
        self.manufacturer_name = manufacturer_name
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Carrega mega-prompt
        self.mega_prompt = self._load_mega_prompt(mega_prompt_path)

        # Inicializa APIs
        self._init_ai_clients()

        # Configurações
        self.min_delay = int(os.getenv("SCRAPING_DELAY_MIN", "2"))
        self.max_delay = int(os.getenv("SCRAPING_DELAY_MAX", "5"))
        self.min_image_quality = 800  # pixels

        # Resultados
        self.products_found = 0
        self.images_downloaded = 0
        self.errors = []

    def _load_mega_prompt(self, path: str) -> str:
        """Carrega contexto do mega-prompt"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Mega-prompt não encontrado em {path}")
            return ""

    def _init_ai_clients(self):
        """Inicializa clientes Gemini e OpenAI"""
        # Gemini com fallback para segunda key
        self.gemini_keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
        ]
        self.current_gemini_key = 0
        genai.configure(api_key=self.gemini_keys[0])
        self.gemini_model = genai.GenerativeModel("gemini-pro")

        # OpenAI
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=10))
    async def _ask_gemini(self, prompt: str) -> str:
        """Consulta Gemini com retry e fallback para segunda key"""
        try:
            response = self.gemini_model.generate_content(prompt)
            await asyncio.sleep(2)  # Rate limiting
            return response.text
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                # Tenta segunda key
                self.current_gemini_key = 1 - self.current_gemini_key
                genai.configure(api_key=self.gemini_keys[self.current_gemini_key])
                logger.info(f"Switching to Gemini key {self.current_gemini_key + 1}")
                raise
            else:
                logger.error(f"Gemini error: {e}")
                raise

    async def _navigate_to_products(self, page: Page) -> List[str]:
        """
        Usa IA para identificar links de produtos no site
        Implementa heurísticas do mega-prompt (Fase 1)
        """
        await page.goto(self.base_url, wait_until="networkidle")
        await asyncio.sleep(self.min_delay)

        # Extrai HTML
        content = await page.content()

        # Monta prompt com contexto
        prompt = f"""
{self.mega_prompt}

TAREFA: Analise o HTML abaixo do site {self.manufacturer_name} ({self.base_url}) e identifique links para páginas de produtos.

Heurísticas (do mega-prompt):
✅ URLs com padrões: /products/, /solucoes/, /equipamentos/, /categoria/
✅ Links com palavras-chave: inversor, módulo, painel, bateria
✅ Breadcrumbs indicando navegação de catálogo
✅ Presença de grids/listas de produtos

❌ Evite: /sobre, /contato, /blog, /noticias, /carreiras

HTML (primeiros 10000 chars):
{content[:10000]}

RESPOSTA (JSON):
{{
  "product_urls": ["url1", "url2", ...],
  "confidence": 0.0-1.0,
  "reasoning": "explicação breve"
}}
"""

        try:
            response = await self._ask_gemini(prompt)
            # Parse JSON da resposta
            result = json.loads(
                response.strip().replace("```json", "").replace("```", "")
            )

            product_urls = result.get("product_urls", [])
            confidence = result.get("confidence", 0.5)

            logger.info(
                f"Found {len(product_urls)} product URLs (confidence: {confidence:.2f})"
            )

            return product_urls[:50]  # Limita a 50 URLs

        except Exception as e:
            logger.error(f"Error in _navigate_to_products: {e}")
            # Fallback: busca heurística simples
            return await self._fallback_product_detection(page)

    async def _fallback_product_detection(self, page: Page) -> List[str]:
        """Detecção de produtos via heurísticas simples (sem IA)"""
        links = await page.query_selector_all("a[href]")

        product_patterns = [
            "/produto",
            "/product",
            "/equipamento",
            "/solucoes",
            "/inversores",
            "/paineis",
            "/baterias",
            "/kits",
        ]

        product_urls = []
        for link in links[:100]:
            href = await link.get_attribute("href")
            if href and any(pattern in href.lower() for pattern in product_patterns):
                if href.startswith("/"):
                    href = self.base_url.rstrip("/") + href
                product_urls.append(href)

        return list(set(product_urls))[:30]

    def _score_image(self, img_url: str, img_element_html: str, img_size: tuple) -> int:
        """
        Aplica sistema de pontuação de 10 pontos do mega-prompt
        """
        score = 0
        width, height = img_size

        # Score 10: Imagens técnicas de alta qualidade
        if width >= 1000 and height >= 1000:
            if any(
                kw in img_url.lower() for kw in ["product", "technical", "datasheet"]
            ):
                score = 10

        # Score 8: Galerias de produtos
        if width >= 800 and height >= 800:
            if "gallery" in img_element_html or "zoom" in img_element_html:
                score = max(score, 8)

        # Score 7: Diagramas técnicos
        if any(kw in img_url.lower() for kw in ["diagram", "esquema", "circuito"]):
            score = max(score, 7)

        # Score 5: Imagens contextuais
        if width >= 600 and height >= 400:
            score = max(score, 5)

        # Score 0: Banners, logos, ícones
        if any(kw in img_url.lower() for kw in ["banner", "logo", "icon", "sprite"]):
            score = 0

        if width < 300 or height < 300:
            score = 0

        return score

    async def _extract_product_images(self, page: Page, product_url: str) -> Dict:
        """
        Extrai imagens de uma página de produto (Fase 3 do mega-prompt)
        """
        try:
            await page.goto(product_url, wait_until="networkidle")
            await asyncio.sleep(self.min_delay)

            # Extrai metadados do produto
            title = await page.title()
            content = await page.content()
            soup = BeautifulSoup(content, "lxml")

            # Busca especificações técnicas
            specs = {}
            spec_tables = soup.find_all(["table", "dl"])
            for table in spec_tables[:3]:
                # Parse tabelas de specs
                rows = table.find_all(["tr", "dt"])
                for row in rows[:10]:
                    cells = row.find_all(["td", "dd", "th", "dt"])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        specs[key] = value

            # Encontra todas as imagens
            images = []
            img_elements = await page.query_selector_all("img")

            for img_el in img_elements:
                src = await img_el.get_attribute("src")
                if not src:
                    continue

                # Normaliza URL
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = self.base_url.rstrip("/") + src

                # Verifica dimensões
                try:
                    bbox = await img_el.bounding_box()
                    if not bbox:
                        continue

                    img_size = (int(bbox["width"]), int(bbox["height"]))

                    # Score da imagem
                    img_html = await img_el.evaluate("el => el.outerHTML")
                    score = self._score_image(src, img_html, img_size)

                    if score >= 5:  # Threshold mínimo
                        images.append(
                            {
                                "url": src,
                                "score": score,
                                "width": img_size[0],
                                "height": img_size[1],
                            }
                        )

                except Exception as e:
                    logger.debug(f"Error processing image: {e}")

            # Ordena por score
            images.sort(key=lambda x: x["score"], reverse=True)

            return {
                "product_url": product_url,
                "title": title,
                "specs": specs,
                "images": images[:10],  # Top 10
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error extracting from {product_url}: {e}")
            self.errors.append({"url": product_url, "error": str(e)})
            return None

    async def _download_image(self, img_data: Dict, product_id: str) -> Optional[str]:
        """Download e validação de qualidade da imagem"""
        import requests
        from io import BytesIO

        try:
            response = requests.get(img_data["url"], timeout=30)
            response.raise_for_status()

            # Abre imagem
            img = Image.open(BytesIO(response.content))

            # Valida qualidade
            if (
                img.width < self.min_image_quality
                or img.height < self.min_image_quality
            ):
                logger.debug(f"Image too small: {img.width}x{img.height}")
                return None

            # Salva
            filename = f"{product_id}_score{img_data['score']}_{img_data['width']}x{img_data['height']}.jpg"
            filepath = self.output_dir / filename

            img.save(filepath, "JPEG", quality=95)
            self.images_downloaded += 1

            return str(filepath)

        except Exception as e:
            logger.error(f"Error downloading {img_data['url']}: {e}")
            return None

    async def scrape(self, max_products: int = 100) -> Dict:
        """
        Método principal de scraping
        """
        logger.info(f"Starting scrape of {self.manufacturer_name}")
        logger.info(f"Base URL: {self.base_url}")

        metadata_list = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="YSH-Solar-Bot/1.0 (+https://yshsolar.com.br/bot)"
            )

            # Fase 1: Navega para catálogo de produtos
            product_urls = await self._navigate_to_products(page)
            logger.info(f"Found {len(product_urls)} product pages")

            # Fase 2-3: Extrai imagens de cada produto
            for i, product_url in enumerate(product_urls[:max_products]):
                logger.info(
                    f"Processing product {i+1}/{len(product_urls)}: {product_url}"
                )

                product_data = await self._extract_product_images(page, product_url)

                if product_data and product_data["images"]:
                    self.products_found += 1

                    # Download top 3 images
                    downloaded_paths = []
                    for img_data in product_data["images"][:3]:
                        path = await self._download_image(img_data, f"product_{i}")
                        if path:
                            downloaded_paths.append(path)

                    product_data["downloaded_images"] = downloaded_paths
                    metadata_list.append(product_data)

                # Rate limiting
                await asyncio.sleep(self.min_delay)

            await browser.close()

        # Salva metadata JSON
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Scraping complete. Products: {self.products_found}, Images: {self.images_downloaded}"
        )

        return {
            "manufacturer": self.manufacturer_name,
            "products_found": self.products_found,
            "images_downloaded": self.images_downloaded,
            "errors": len(self.errors),
            "metadata_file": str(metadata_file),
        }


async def main():
    parser = argparse.ArgumentParser(description="AI-Guided Product Image Scraper")
    parser.add_argument("--manufacturer", required=True, help="Manufacturer name")
    parser.add_argument("--url", required=True, help="Base URL")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument(
        "--max-products", type=int, default=100, help="Max products to scrape"
    )

    args = parser.parse_args()

    scraper = AIGuidedScraper(
        manufacturer_name=args.manufacturer,
        base_url=args.url,
        output_dir=args.output_dir,
    )

    result = await scraper.scrape(max_products=args.max_products)

    # Output JSON para o Dagster
    print(json.dumps(result))

    return 0 if result["products_found"] > 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
