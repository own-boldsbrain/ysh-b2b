#!/usr/bin/env python3
"""
Script para captura de imagens dinâmicas de produtos usando Playwright.
Renderiza JavaScript e extrai imagens após carregamento completo da página.
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
from playwright.async_api import Page, async_playwright


@dataclass
class ProductImage:
    """Representa uma imagem de produto capturada."""

    url: str
    alt: str
    width: int
    height: int
    is_product_image: bool


@dataclass
class ScrapingResult:
    """Resultado do scraping de um produto."""

    manufacturer: str
    model: str
    images: list[ProductImage]
    pdfs: list[str]
    success: bool
    error: Optional[str] = None


class ManufacturerScraper:
    """Base class para scrapers específicos de fabricantes."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_product_images(self, page: Page, model: str) -> list[ProductImage]:
        """Extrai imagens de produto da página. Override em subclasses."""
        raise NotImplementedError

    async def get_pdfs(self, page: Page) -> list[str]:
        """Extrai links de PDFs da página."""
        pdfs = []
        pdf_links = await page.locator('a[href*=".pdf"]').all()

        for link in pdf_links:
            href = await link.get_attribute("href")
            if href:
                full_url = urljoin(self.base_url, href)
                pdfs.append(full_url)

        return pdfs

    def is_valid_product_image(self, img: ProductImage) -> bool:
        """Valida se é uma imagem de produto relevante."""
        # Rejeitar imagens muito pequenas (logos, ícones)
        if img.width < 200 or img.height < 200:
            return False

        # Rejeitar URLs com padrões de não-produto
        excluded = ["logo", "icon", "banner", "avatar", "badge", "sprite"]
        url_lower = img.url.lower()

        for pattern in excluded:
            if pattern in url_lower and "product" not in url_lower:
                return False

        return True


class HuaweiScraper(ManufacturerScraper):
    """Scraper específico para Huawei Solar."""

    def __init__(self):
        super().__init__("https://solar.huawei.com/br")

    async def get_product_images(self, page: Page, model: str) -> list[ProductImage]:
        """Extrai imagens de produtos Huawei."""
        images = []

        # Aguardar carregamento de imagens
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Selecionar imagens de produto
        img_selectors = [
            ".product-image img",
            ".product-detail-image img",
            ".product-gallery img",
            '[class*="product"] img',
            '[class*="inverter"] img',
        ]

        for selector in img_selectors:
            try:
                img_elements = await page.locator(selector).all()

                for img in img_elements:
                    src = await img.get_attribute("src")
                    if not src or src.startswith("data:"):
                        # Tentar data-src para lazy loading
                        src = await img.get_attribute("data-src")

                    if not src:
                        continue

                    # Construir URL completa
                    full_url = urljoin(self.base_url, src)

                    # Obter dimensões
                    box = await img.bounding_box()
                    width = int(box["width"]) if box else 0
                    height = int(box["height"]) if box else 0

                    # Obter alt text
                    alt = await img.get_attribute("alt") or ""

                    product_img = ProductImage(
                        url=full_url,
                        alt=alt,
                        width=width,
                        height=height,
                        is_product_image=True,
                    )

                    if self.is_valid_product_image(product_img):
                        images.append(product_img)

            except Exception as e:
                print(f"   ⚠️  Erro ao processar seletor {selector}: {e}")
                continue

        return images


class DeyeScraper(ManufacturerScraper):
    """Scraper específico para Deye."""

    def __init__(self):
        super().__init__("https://pt.deyeinverter.com")

    async def get_product_images(self, page: Page, model: str) -> list[ProductImage]:
        """Extrai imagens de produtos Deye."""
        images = []

        await page.wait_for_load_state("networkidle", timeout=10000)

        # Seletores específicos para Deye
        img_selectors = [
            ".product-img img",
            ".product-image img",
            '[class*="product"] img[src*="inverter"]',
            ".swiper-slide img",
        ]

        for selector in img_selectors:
            try:
                img_elements = await page.locator(selector).all()

                for img in img_elements:
                    src = (
                        await img.get_attribute("src")
                        or await img.get_attribute("data-src")
                        or await img.get_attribute("data-lazy-src")
                    )

                    if not src or src.startswith("data:"):
                        continue

                    full_url = urljoin(self.base_url, src)
                    box = await img.bounding_box()
                    width = int(box["width"]) if box else 0
                    height = int(box["height"]) if box else 0
                    alt = await img.get_attribute("alt") or ""

                    product_img = ProductImage(
                        url=full_url,
                        alt=alt,
                        width=width,
                        height=height,
                        is_product_image=True,
                    )

                    if self.is_valid_product_image(product_img):
                        images.append(product_img)

            except Exception:
                continue

        return images


class GrowattScraper(ManufacturerScraper):
    """Scraper específico para Growatt."""

    def __init__(self):
        super().__init__("https://br.growatt.com")

    async def get_product_images(self, page: Page, model: str) -> list[ProductImage]:
        """Extrai imagens de produtos Growatt."""
        images = []

        await page.wait_for_load_state("networkidle", timeout=10000)

        img_selectors = [
            ".product-image img",
            ".product-detail img",
            '[class*="product"] img',
        ]

        for selector in img_selectors:
            try:
                img_elements = await page.locator(selector).all()

                for img in img_elements:
                    src = await img.get_attribute("src") or await img.get_attribute(
                        "data-src"
                    )

                    if not src or src.startswith("data:"):
                        continue

                    full_url = urljoin(self.base_url, src)
                    box = await img.bounding_box()
                    width = int(box["width"]) if box else 0
                    height = int(box["height"]) if box else 0
                    alt = await img.get_attribute("alt") or ""

                    product_img = ProductImage(
                        url=full_url,
                        alt=alt,
                        width=width,
                        height=height,
                        is_product_image=True,
                    )

                    if self.is_valid_product_image(product_img):
                        images.append(product_img)

            except Exception:
                continue

        return images


class SungrowScraper(ManufacturerScraper):
    """Scraper específico para Sungrow."""

    def __init__(self):
        super().__init__("https://en.sungrowpower.com")

    async def get_product_images(self, page: Page, model: str) -> list[ProductImage]:
        """Extrai imagens de produtos Sungrow."""
        images = []

        await page.wait_for_load_state("networkidle", timeout=10000)

        img_selectors = [
            ".product-img img",
            '[class*="product"] img',
            ".detail-image img",
        ]

        for selector in img_selectors:
            try:
                img_elements = await page.locator(selector).all()

                for img in img_elements:
                    src = await img.get_attribute("src") or await img.get_attribute(
                        "data-src"
                    )

                    if not src or src.startswith("data:"):
                        continue

                    full_url = urljoin(self.base_url, src)
                    box = await img.bounding_box()
                    width = int(box["width"]) if box else 0
                    height = int(box["height"]) if box else 0
                    alt = await img.get_attribute("alt") or ""

                    product_img = ProductImage(
                        url=full_url,
                        alt=alt,
                        width=width,
                        height=height,
                        is_product_image=True,
                    )

                    if self.is_valid_product_image(product_img):
                        images.append(product_img)

            except Exception:
                continue

        return images


class ImageDownloader:
    """Baixa e salva imagens de produtos."""

    def __init__(self, download_dir: Path):
        self.download_dir = download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_image(
        self, url: str, manufacturer: str, model: str
    ) -> Optional[Path]:
        """Baixa uma imagem e salva localmente."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        # Determinar extensão do arquivo
                        content_type = response.headers.get("content-type", "")
                        ext = ".jpg"
                        if "png" in content_type:
                            ext = ".png"
                        elif "webp" in content_type:
                            ext = ".webp"

                        # Criar nome de arquivo seguro
                        safe_model = (
                            model.replace("/", "_").replace(" ", "_").replace("\\", "_")
                        )
                        filename = (
                            f"{manufacturer}_{safe_model}_{hash(url) % 10000}{ext}"
                        )
                        filepath = self.download_dir / filename

                        # Salvar arquivo
                        content = await response.read()
                        with open(filepath, "wb") as f:
                            f.write(content)

                        return filepath

        except Exception as e:
            print(f"   ⚠️  Erro ao baixar {url}: {e}")

        return None

    async def download_images(
        self, images: list[ProductImage], manufacturer: str, model: str
    ) -> list[Path]:
        """Baixa múltiplas imagens em paralelo."""
        tasks = [self.download_image(img.url, manufacturer, model) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar resultados válidos
        downloaded = [r for r in results if isinstance(r, Path)]
        return downloaded


class DynamicImageScraper:
    """Orquestrador de scraping dinâmico com Playwright."""

    def __init__(self, download_images: bool = True):
        self.scrapers = {
            "huawei": HuaweiScraper(),
            "deye": DeyeScraper(),
            "growatt": GrowattScraper(),
            "sungrow": SungrowScraper(),
        }
        self.download_images = download_images

    def get_scraper(self, manufacturer: str) -> Optional[ManufacturerScraper]:
        """Retorna scraper específico para o fabricante."""
        return self.scrapers.get(manufacturer.lower())

    async def search_product_page(
        self, page: Page, manufacturer: str, model: str
    ) -> Optional[str]:
        """Busca URL da página do produto usando pesquisa do site."""
        scraper = self.get_scraper(manufacturer)
        if not scraper:
            return None

        try:
            # Ir para página inicial
            await page.goto(scraper.base_url, timeout=15000)

            # Tentar encontrar campo de busca
            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="search" i]',
                'input[name*="search" i]',
                ".search-input",
            ]

            for selector in search_selectors:
                try:
                    search_input = page.locator(selector).first
                    if await search_input.count() > 0:
                        await search_input.fill(model)
                        await search_input.press("Enter")
                        await page.wait_for_load_state("networkidle")

                        # Tentar clicar no primeiro resultado
                        result_selectors = [
                            ".product-item a",
                            '[class*="product"] a',
                            ".search-result a",
                        ]

                        for result_sel in result_selectors:
                            results = page.locator(result_sel)
                            if await results.count() > 0:
                                await results.first.click()
                                await page.wait_for_load_state("networkidle")
                                return page.url

                except Exception:
                    continue

        except Exception as e:
            print(f"   ⚠️  Erro ao buscar produto: {e}")

        return None

    async def scrape_product(
        self, manufacturer: str, model: str, product_url: Optional[str] = None
    ) -> ScrapingResult:
        """Scrape imagens e PDFs de um produto específico."""
        scraper = self.get_scraper(manufacturer)

        if not scraper:
            return ScrapingResult(
                manufacturer=manufacturer,
                model=model,
                images=[],
                pdfs=[],
                success=False,
                error=f"Scraper não implementado para {manufacturer}",
            )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )
                page = await context.new_page()

                # Navegar para URL do produto ou buscar
                if product_url:
                    await page.goto(product_url, timeout=15000)
                else:
                    found_url = await self.search_product_page(
                        page, manufacturer, model
                    )
                    if not found_url:
                        return ScrapingResult(
                            manufacturer=manufacturer,
                            model=model,
                            images=[],
                            pdfs=[],
                            success=False,
                            error="Página do produto não encontrada",
                        )

                # Extrair imagens e PDFs
                images = await scraper.get_product_images(page, model)
                pdfs = await scraper.get_pdfs(page)

                await browser.close()

                return ScrapingResult(
                    manufacturer=manufacturer,
                    model=model,
                    images=images,
                    pdfs=pdfs,
                    success=True,
                )

        except Exception as e:
            return ScrapingResult(
                manufacturer=manufacturer,
                model=model,
                images=[],
                pdfs=[],
                success=False,
                error=str(e),
            )


async def scrape_products_from_inventory(
    inventory_path: Path,
    output_path: Path,
    download_dir: Path,
    limit: int = 10,
    download: bool = True,
):
    """Scrape imagens de produtos do inventário usando Playwright."""
    print("🚀 Iniciando scraping dinâmico com Playwright\n")

    # Carregar inventário
    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    scraper = DynamicImageScraper(download_images=download)
    downloader = ImageDownloader(download_dir) if download else None
    results = []
    total_images = 0
    total_pdfs = 0
    total_downloaded = 0
    successful = 0

    # Processar produtos (limitado)
    processed = 0
    for manufacturer_key, products in inventory["products"].items():
        if processed >= limit:
            break

        for product in products:
            if processed >= limit:
                break

            manufacturer = product.get("manufacturer", "")
            model = product.get("model", "")

            print(f"📦 Processando: {manufacturer} {model}")

            result = await scraper.scrape_product(manufacturer, model)

            if result.success:
                successful += 1
                total_images += len(result.images)
                total_pdfs += len(result.pdfs)

                print(f"   ✅ {len(result.images)} imagens | {len(result.pdfs)} PDFs")

                # Baixar imagens se solicitado
                if download and downloader and result.images:
                    print(f"   📥 Baixando {len(result.images)} imagens...")
                    downloaded = await downloader.download_images(
                        result.images, manufacturer, model
                    )
                    total_downloaded += len(downloaded)
                    print(f"   💾 {len(downloaded)} imagens salvas localmente")

                # Atualizar produto no inventário
                if result.images:
                    if "resources" not in product:
                        product["resources"] = {"datasheets": [], "images": []}

                    product["resources"]["images"] = [img.url for img in result.images]
                    product["image_status"] = "found"

                if result.pdfs:
                    if "resources" not in product:
                        product["resources"] = {"datasheets": [], "images": []}

                    product["resources"]["datasheets"].extend(result.pdfs)
                    product["datasheet_status"] = "found"

            else:
                print(f"   ❌ Erro: {result.error}")

            results.append(result)
            processed += 1

    # Salvar inventário atualizado
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    # Relatório final
    print("\n" + "=" * 70)
    print("📊 RESUMO DO SCRAPING DINÂMICO")
    print("=" * 70)
    print(f"Produtos processados: {processed}")
    print(f"Sucessos: {successful} ({successful/processed*100:.1f}%)")
    print(f"Total de imagens encontradas: {total_images}")
    if download:
        print(f"Total de imagens baixadas: {total_downloaded}")
    print(f"Total de PDFs encontrados: {total_pdfs}")
    print(f"\n✅ Inventário atualizado: {output_path}")
    if download:
        print(f"📁 Imagens salvas em: {download_dir}")


async def main():
    """Execução principal."""
    base_path = Path(__file__).parent.parent

    inventory_path = base_path / "data" / "products_inventory_raw.json"
    output_path = base_path / "data" / "products_inventory_dynamic_enriched.json"
    download_dir = base_path / "data" / "products-resources" / "images"

    if not inventory_path.exists():
        print(f"❌ Arquivo não encontrado: {inventory_path}")
        return

    # Processar primeiros 5 produtos como teste
    await scrape_products_from_inventory(
        inventory_path, output_path, download_dir, limit=5, download=True
    )


if __name__ == "__main__":
    asyncio.run(main())
