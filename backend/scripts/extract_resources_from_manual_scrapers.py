"""
Extrator de recursos de HTMLs salvos manualmente
=================================================

Parseia arquivos HTML em data/products-inventory/scrapers-inverters
e extrai URLs de imagens e PDFs de produtos de inversores.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Configurações
SCRAPERS_DIR = Path("data/products-inventory/scrapers-inverters")
OUTPUT_FILE = Path("data/products-resources/manual_scraped_resources.json")

# Mapeamento de fabricantes por palavras-chave nos arquivos
MANUFACTURER_KEYWORDS = {
    "huawei": ["huawei", "sun2000"],
    "deye": ["deye"],
    "sungrow": ["sungrow"],
    "growatt": ["growatt"],
    "apsystems": ["apsystems", "apsystem"],
    "solis": ["solis", "solisinverters"],
}


def identify_manufacturer(filename: str, content: str) -> str:
    """Identifica fabricante pelo nome do arquivo ou conteúdo."""
    filename_lower = filename.lower()
    content_lower = content.lower()[:2000]  # Primeiros 2000 chars

    for manufacturer, keywords in MANUFACTURER_KEYWORDS.items():
        if any(kw in filename_lower or kw in content_lower for kw in keywords):
            return manufacturer

    return "unknown"


def extract_base_url(html_content: str) -> str:
    """Extrai URL base do comentário SingleFile."""
    match = re.search(r"url:\s*(https?://[^\s]+)", html_content)
    if match:
        return match.group(1).strip()
    return ""


def extract_product_images(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extrai URLs de imagens de produtos."""
    images: Set[str] = set()

    # Padrões de classes comuns para imagens de produtos
    product_img_patterns = [
        "product-image",
        "product-img",
        "product-photo",
        "item-image",
        "goods-img",
        "productImg",
        "pro-img",
    ]

    # 1. Buscar TODAS as imagens grandes primeiro
    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-original")
            or img.get("data-lazy-src")
        )
        if src and isinstance(src, str):
            full_url = urljoin(base_url, src)
            if _is_valid_product_image(full_url):
                images.add(full_url)

    # 2. Buscar por classes específicas
    for pattern in product_img_patterns:
        for img in soup.find_all("img", class_=re.compile(pattern, re.I)):
            src = img.get("src") or img.get("data-src") or img.get("data-original")
            if src and isinstance(src, str):
                full_url = urljoin(base_url, src)
                if _is_valid_product_image(full_url):
                    images.add(full_url)

    # 2. Buscar imagens em containers de produtos
    product_containers = soup.find_all(
        ["div", "li", "article"],
        class_=re.compile(r"product|item|goods", re.I),
    )
    for container in product_containers:
        for img in container.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-original")
            if src:
                full_url = urljoin(base_url, src)
                if _is_valid_product_image(full_url):
                    images.add(full_url)

    # 3. Buscar em <picture> tags
    for picture in soup.find_all("picture"):
        for source in picture.find_all("source"):
            srcset = source.get("srcset")
            if srcset:
                # Pegar primeira URL do srcset
                first_url = srcset.split(",")[0].strip().split()[0]
                full_url = urljoin(base_url, first_url)
                if _is_valid_product_image(full_url):
                    images.add(full_url)

    return sorted(images)


def extract_pdf_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extrai URLs de PDFs (datasheets, manuais)."""
    pdfs: Set[str] = set()

    # 1. Links diretos para PDF
    for link in soup.find_all("a", href=re.compile(r"\.pdf$", re.I)):
        href = link.get("href")
        if href:
            full_url = urljoin(base_url, href)
            pdfs.add(full_url)

    # 2. Links com texto indicando datasheet/manual
    pdf_keywords = [
        "datasheet",
        "manual",
        "specification",
        "download",
        "catalog",
        "brochure",
        "guia",
        "documento",
    ]

    for link in soup.find_all("a"):
        href = link.get("href", "")
        text = link.get_text().lower()

        if any(kw in text or kw in href.lower() for kw in pdf_keywords):
            if href and (".pdf" in href.lower() or "download" in href.lower()):
                full_url = urljoin(base_url, href)
                if _is_valid_pdf_url(full_url):
                    pdfs.add(full_url)

    # 3. Buscar em botões de download
    for button in soup.find_all(
        ["button", "span"], class_=re.compile(r"download", re.I)
    ):
        parent = button.find_parent("a")
        if parent:
            href = parent.get("href")
            if href:
                full_url = urljoin(base_url, href)
                if _is_valid_pdf_url(full_url):
                    pdfs.add(full_url)

    return sorted(pdfs)


def _is_valid_product_image(url: str) -> bool:
    """Valida se URL é uma imagem de produto válida."""
    if not url or url.startswith("data:"):
        return False

    # Excluir ícones, logos, banners pequenos, SVGs
    excluded_patterns = [
        "icon",
        "logo",
        "banner",
        "sprite",
        "placeholder",
        "loading",
        "thumbnail",
        ".svg",
        "avatar",
        "badge",
    ]

    url_lower = url.lower()
    if any(pattern in url_lower for pattern in excluded_patterns):
        # Permitir se contiver "product" explicitamente
        if "product" not in url_lower and "inverter" not in url_lower:
            return False

    # Verificar extensões de imagem
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif")
    parsed = urlparse(url)
    path_lower = parsed.path.lower()

    # Aceitar se tiver extensão válida OU parâmetros de imagem
    has_valid_ext = any(path_lower.endswith(ext) for ext in valid_extensions)
    has_img_param = any(ext in url_lower for ext in [".jpg", ".jpeg", ".png", ".webp"])

    return has_valid_ext or has_img_param


def _is_valid_pdf_url(url: str) -> bool:
    """Valida se URL é um PDF válido."""
    if not url:
        return False

    url_lower = url.lower()
    return ".pdf" in url_lower or "download" in url_lower


def process_html_files() -> Dict:
    """Processa todos os HTMLs e extrai recursos."""
    results = {
        "metadata": {
            "source_directory": str(SCRAPERS_DIR),
            "total_files_processed": 0,
        },
        "by_manufacturer": {},
    }

    if not SCRAPERS_DIR.exists():
        print(f"❌ Diretório não encontrado: {SCRAPERS_DIR}")
        return results

    html_files = list(SCRAPERS_DIR.glob("*.html"))
    results["metadata"]["total_files_processed"] = len(html_files)

    print(f"📁 Encontrados {len(html_files)} arquivos HTML\n")

    for html_file in html_files:
        print(f"📄 Processando: {html_file.name}")

        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        manufacturer = identify_manufacturer(html_file.name, content)
        base_url = extract_base_url(content)

        print(f"   Fabricante: {manufacturer}")
        print(f"   URL base: {base_url}")

        images = extract_product_images(soup, base_url)
        pdfs = extract_pdf_links(soup, base_url)

        print(f"   ✓ {len(images)} imagens | {len(pdfs)} PDFs\n")

        if manufacturer not in results["by_manufacturer"]:
            results["by_manufacturer"][manufacturer] = {
                "images": [],
                "pdfs": [],
                "source_files": [],
            }

        results["by_manufacturer"][manufacturer]["images"].extend(images)
        results["by_manufacturer"][manufacturer]["pdfs"].extend(pdfs)
        results["by_manufacturer"][manufacturer]["source_files"].append(html_file.name)

    # Remover duplicatas
    for manufacturer in results["by_manufacturer"]:
        data = results["by_manufacturer"][manufacturer]
        data["images"] = sorted(set(data["images"]))
        data["pdfs"] = sorted(set(data["pdfs"]))

        print(
            f"🏭 {manufacturer.upper()}: "
            f"{len(data['images'])} imagens únicas | "
            f"{len(data['pdfs'])} PDFs únicos"
        )

    return results


def main() -> None:
    print("🚀 Iniciando extração de recursos de scrapers manuais\n")

    results = process_html_files()

    # Salvar resultados
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Resultados salvos em: {OUTPUT_FILE}")

    # Estatísticas totais
    total_images = sum(
        len(data["images"]) for data in results["by_manufacturer"].values()
    )
    total_pdfs = sum(len(data["pdfs"]) for data in results["by_manufacturer"].values())

    print(f"\n📊 TOTAL: {total_images} imagens | {total_pdfs} PDFs")


if __name__ == "__main__":
    main()
