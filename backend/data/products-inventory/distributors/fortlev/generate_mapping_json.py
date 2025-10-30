#!/usr/bin/env python3
"""
Gera um arquivo JSON de mapeamento completo de imagens renomeadas.
"""
import json
import os
import re
from pathlib import Path

# Caminhos
INVERTERS_JSON = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\products-inventory-backup-20251017-134630\distributors\fortlev\fortlev-inverters.json"
RENAMED_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\organized_images\inverters_renamed_v2"
OUTPUT_JSON = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\inverters_image_mapping_complete.json"


def extract_image_codes(image_url):
    """Extrai todos os códigos IIN possíveis da URL."""
    if not image_url:
        return []
    codes = re.findall(r"IIN\d{5}", image_url)
    return list(set(codes))


def main():
    # Carregar dados dos inversores
    with open(INVERTERS_JSON, "r", encoding="utf-8") as f:
        inverters = json.load(f)

    # Criar mapeamento completo
    complete_mapping = []

    for inverter in inverters:
        image_codes = extract_image_codes(inverter.get("image", ""))

        if image_codes:
            # Nome do arquivo renomeado
            manufacturer = inverter.get("manufacturer", "Unknown").upper()
            name = inverter.get("name", "")
            name_clean = (
                name.replace("ON-GRID", "")
                .replace("GRID-TIE", "")
                .replace("OFF-GRID", "")
                .strip()
            )
            new_name = f"{manufacturer}_{name_clean}".replace(" ", "_")

            # Limitar tamanho
            if len(new_name) > 100:
                new_name = new_name[:100]

            # Extrair especificações técnicas do nome
            specs = {}

            # Extrair potência
            power_match = re.search(r"(\d+\.?\d*)KW", name, re.IGNORECASE)
            if power_match:
                specs["power_kw"] = float(power_match.group(1))

            # Extrair voltagem
            voltage_match = re.search(r"(\d+)V", name)
            if voltage_match:
                specs["voltage_v"] = int(voltage_match.group(1))

            # Extrair número de MPPTs
            mppt_match = re.search(r"(\d+)\s*MPPT", name, re.IGNORECASE)
            if mppt_match:
                specs["mppt_count"] = int(mppt_match.group(1))

            # Determinar tipo
            if "HYBRID" in name.upper():
                specs["type"] = "HYBRID"
            elif "OFF-GRID" in name.upper():
                specs["type"] = "OFF_GRID"
            elif "GRID" in name.upper() or "ON-GRID" in name.upper():
                specs["type"] = "GRID_TIE"
            else:
                specs["type"] = "UNKNOWN"

            # Determinar fases
            if "MONOFÁSICO" in name.upper() or "220V" in name:
                specs["phases"] = "Monofásico"
            elif "TRIFÁSICO" in name.upper() or "380V" in name:
                specs["phases"] = "Trifásico"

            # Extrair preço
            price_value = None
            if inverter.get("price", "").startswith("R$"):
                try:
                    price_str = (
                        inverter["price"]
                        .replace("R$", "")
                        .replace(".", "")
                        .replace(",", ".")
                        .strip()
                    )
                    price_value = float(price_str)
                except:
                    pass

            mapping_entry = {
                "product_id": inverter.get("id"),
                "name": inverter.get("name"),
                "manufacturer": inverter.get("manufacturer"),
                "image_codes": image_codes,
                "original_image_url": inverter.get("image"),
                "renamed_filename": f"{new_name}.png",
                "price_brl": price_value,
                "technical_specs": specs,
                "category": "inverters",
                "source": "fortlevsolar.app",
            }

            complete_mapping.append(mapping_entry)

    # Salvar JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(complete_mapping, f, ensure_ascii=False, indent=2)

    print(f"Mapeamento completo salvo em: {OUTPUT_JSON}")
    print(f"Total de produtos mapeados: {len(complete_mapping)}")

    # Estatísticas
    with_price = sum(1 for m in complete_mapping if m["price_brl"])
    with_power = sum(1 for m in complete_mapping if "power_kw" in m["technical_specs"])
    with_mppt = sum(1 for m in complete_mapping if "mppt_count" in m["technical_specs"])

    print(f"\nEstatísticas:")
    print(f"  - Produtos com preço: {with_price}")
    print(f"  - Produtos com potência identificada: {with_power}")
    print(f"  - Produtos com MPPT identificado: {with_mppt}")


if __name__ == "__main__":
    main()
