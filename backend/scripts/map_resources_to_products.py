#!/usr/bin/env python3
"""
Script para mapear recursos extraídos manualmente aos produtos do inventário.
Enriquece product_resources.json com PDFs extraídos dos scrapers HTML.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import unquote


def load_json(file_path: Path) -> dict:
    """Carrega arquivo JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, file_path: Path) -> None:
    """Salva arquivo JSON formatado."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_model_from_url(url: str) -> list[str]:
    """
    Extrai identificadores de modelo/potência de URL de PDF.

    Exemplos:
    - manual_sun-29.9-50k-sg01hp3-eu-bm4_20250808_pt.pdf → ["sun-29.9-50k", "29.9k", "50k"]
    - manual_sun-3.6-6k-og01lp1-eu-am2_20250915_pt.pdf → ["sun-3.6-6k", "3.6k", "6k"]

    Returns:
        Lista de identificadores extraídos (vazya se nenhum encontrado)
    """
    # Decodificar caracteres especiais
    url_decoded = unquote(url)
    identifiers = []

    # Padrão para manuais Deye: manual_sun-{potência}k-...
    # Ex: manual_sun-29.9-50k ou manual_sun-3.6-6k
    deye_pattern = r"manual_sun-([\d.]+-[\d.]+k)"
    match = re.search(deye_pattern, url_decoded, re.IGNORECASE)
    if match:
        full_range = match.group(1)  # Ex: "29.9-50k" ou "3.6-6k"
        identifiers.append(f"sun-{full_range}")

        # Extrair potências individuais
        powers = re.findall(r"([\d.]+)k", full_range, re.IGNORECASE)
        identifiers.extend([f"{p}k" for p in powers])

    # Padrão genérico: buscar por números seguidos de kW/K
    power_pattern = r"(\d+(?:\.\d+)?)\s*k[wW]?"
    for match in re.finditer(power_pattern, url_decoded, re.IGNORECASE):
        power_id = f"{match.group(1)}k"
        if power_id not in identifiers:
            identifiers.append(power_id)

    return identifiers


def normalize_manufacturer_name(name: str) -> str:
    """Normaliza nome de fabricante para comparação."""
    return name.lower().strip().replace(" ", "").replace("-", "")


def match_product_to_resource(
    product: dict, resources: List[str], manufacturer: str
) -> List[str]:
    """
    Mapeia recursos (PDFs) a um produto específico.

    Args:
        product: Dicionário com dados do produto
        resources: Lista de URLs de recursos
        manufacturer: Nome do fabricante

    Returns:
        Lista de URLs que correspondem ao produto
    """
    matched = []
    model = product.get("model", "").lower()
    power = product.get("power", "").lower().replace("kw", "k")

    for url in resources:
        url_lower = url.lower()

        # Match direto por modelo
        if model and model in url_lower:
            matched.append(url)
            continue

        # Match por potência extraída da URL
        extracted_identifiers = extract_model_from_url(url)
        for identifier in extracted_identifiers:
            if power and power in identifier.lower():
                matched.append(url)
                break

    return matched


def enrich_product_resources(
    inventory_path: Path,
    manual_resources_path: Path,
    output_path: Path,
) -> Dict:
    """
    Enriquece inventário de produtos com recursos extraídos manualmente.

    Args:
        inventory_path: Caminho para products_inventory_raw.json
        manual_resources_path: Caminho para manual_scraped_resources.json
        output_path: Caminho para salvar resultado enriquecido

    Returns:
        Dicionário com estatísticas do processo
    """
    print("🔄 Carregando arquivos...")
    inventory = load_json(inventory_path)
    manual_resources = load_json(manual_resources_path)

    stats = {
        "total_products": 0,
        "products_enriched": 0,
        "total_resources_mapped": 0,
        "by_manufacturer": {},
    }

    # Criar mapeamento de fabricante para recursos
    manufacturer_resources = {}
    for mfr, data in manual_resources["by_manufacturer"].items():
        if data["pdfs"]:
            manufacturer_resources[mfr] = data["pdfs"]

    print(f"\n📊 Recursos disponíveis por fabricante:")
    for mfr, pdfs in manufacturer_resources.items():
        print(f"   {mfr.upper()}: {len(pdfs)} PDFs")

    print("\n🔗 Mapeando recursos aos produtos...\n")

    # Processar cada fabricante no inventário
    for manufacturer_key, products in inventory["products"].items():
        stats["by_manufacturer"][manufacturer_key] = {
            "total": len(products),
            "enriched": 0,
            "resources_added": 0,
        }

        # Normalizar nome do fabricante
        mfr_normalized = normalize_manufacturer_name(manufacturer_key)

        # Buscar recursos correspondentes
        available_resources = None
        for mfr, pdfs in manufacturer_resources.items():
            if normalize_manufacturer_name(mfr) == mfr_normalized:
                available_resources = pdfs
                break

        if not available_resources:
            print(f"⚠️  {manufacturer_key.upper()}: Sem recursos manuais disponíveis")
            continue

        # Mapear recursos a cada produto
        for product in products:
            stats["total_products"] += 1

            matched_resources = match_product_to_resource(
                product, available_resources, manufacturer_key
            )

            if matched_resources:
                # Adicionar recursos ao produto
                if "resources" not in product:
                    product["resources"] = {"datasheets": [], "images": []}

                # Adicionar PDFs únicos
                existing = set(product["resources"]["datasheets"])
                new_pdfs = [pdf for pdf in matched_resources if pdf not in existing]
                product["resources"]["datasheets"].extend(new_pdfs)

                # Atualizar status
                product["datasheet_status"] = "found"

                # Estatísticas
                stats["products_enriched"] += 1
                stats["by_manufacturer"][manufacturer_key]["enriched"] += 1
                stats["by_manufacturer"][manufacturer_key]["resources_added"] += len(
                    new_pdfs
                )
                stats["total_resources_mapped"] += len(new_pdfs)

                print(
                    f"✅ {manufacturer_key.upper()} {product['model']}: {len(new_pdfs)} PDFs adicionados"
                )

    # Salvar inventário enriquecido
    print(f"\n💾 Salvando inventário enriquecido...")
    save_json(inventory, output_path)

    # Relatório final
    print("\n" + "=" * 70)
    print("📈 RESUMO DO MAPEAMENTO")
    print("=" * 70)
    print(f"Total de produtos processados: {stats['total_products']}")
    print(f"Produtos enriquecidos: {stats['products_enriched']}")
    print(f"Total de recursos mapeados: {stats['total_resources_mapped']}")
    print(f"\nPor fabricante:")
    for mfr, data in stats["by_manufacturer"].items():
        if data["enriched"] > 0:
            print(
                f"  {mfr.upper()}: {data['enriched']}/{data['total']} produtos "
                f"({data['resources_added']} recursos)"
            )

    return stats


def main():
    """Execução principal."""
    base_path = Path(__file__).parent.parent

    inventory_path = base_path / "data" / "products_inventory_raw.json"
    manual_resources_path = (
        base_path / "data" / "products-resources" / "manual_scraped_resources.json"
    )
    output_path = base_path / "data" / "products_inventory_enriched.json"

    if not inventory_path.exists():
        print(f"❌ Arquivo não encontrado: {inventory_path}")
        return

    if not manual_resources_path.exists():
        print(f"❌ Arquivo não encontrado: {manual_resources_path}")
        return

    stats = enrich_product_resources(inventory_path, manual_resources_path, output_path)

    print(f"\n✅ Arquivo salvo: {output_path}")


if __name__ == "__main__":
    main()
