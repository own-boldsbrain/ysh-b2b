"""
Manufacturer Extractor - YSH Unified Inventory
Extrai lista consolidada de fabricantes de todos os componentes
"""

import json
from pathlib import Path
from collections import Counter


def extract_manufacturers(json_file: Path):
    """Extrai fabricantes únicos de todos os produtos."""

    with open(json_file, "r", encoding="utf-8") as f:
        products = json.load(f)

    manufacturers = {"panels": [], "inverters": [], "batteries": [], "all": []}

    for product in products:
        components = product.get("components", {})

        # Painéis
        for panel in components.get("panels", []):
            brand = panel.get("brand") or panel.get("manufacturer")
            if brand and brand not in ["None", "Unknown"]:
                manufacturers["panels"].append(brand)
                manufacturers["all"].append(brand)

        # Inversores
        for inverter in components.get("inverters", []):
            brand = inverter.get("brand") or inverter.get("manufacturer")
            if brand and brand not in ["None", "Unknown"]:
                manufacturers["inverters"].append(brand)
                manufacturers["all"].append(brand)

        # Baterias
        for battery in components.get("batteries", []):
            brand = battery.get("brand")
            if brand and brand not in ["None", "Unknown"]:
                manufacturers["batteries"].append(brand)
                manufacturers["all"].append(brand)

    # Contar ocorrências
    return {
        "panels": Counter(manufacturers["panels"]),
        "inverters": Counter(manufacturers["inverters"]),
        "batteries": Counter(manufacturers["batteries"]),
        "all": Counter(manufacturers["all"]),
    }


def normalize_manufacturer_name(name: str) -> str:
    """Normaliza nome de fabricante."""

    # Remover ruído
    noise_patterns = [
        "<Strong>Kit",
        "Paineis:",
        "Painéis:",
        "Potência:",
        "Potência",
        "Composição:",
        "Energia:",
        "Inversor",
        "Kit",
        "1X",
        "2X",
        "3X",
        "4X",
        "Chumbo",  # Tecnologia, não fabricante
    ]

    if name in noise_patterns:
        return None

    # Padrões que são especificações, não fabricantes
    if any(x in name for x in ["Kw", "KW", "Ah/", "A "]):
        return None

    if name.isdigit():
        return None

    # Normalização de nomes conhecidos
    normalization_map = {
        "ASTRONERGY": "Astronergy",
        "BYD": "BYD",
        "DAH": "DAH Solar",
        "Dah": "DAH Solar",
        "DEYE": "Deye",
        "Deye": "Deye",
        "ENPHASE": "Enphase",
        "Enphase": "Enphase",
        "Epever": "EPever",
        "Freedom": "Freedom",
        "GOODWE": "GoodWe",
        "GROWATT": "Growatt",
        "Growatt": "Growatt",
        "HANERSUN": "Hanersun",
        "HUAWEI": "Huawei",
        "LONGi": "LONGi",
        "Longi": "LONGi",
        "Luxen": "Luxen Solar",
        "MINASOL": "Minasol",
        "Moura": "Moura",
        "OSDA": "OSDA Solar",
        "Osda": "OSDA Solar",
        "Renesola": "ReneSola",
        "Resun": "Resun",
        "Risen": "Risen Energy",
        "SOFAR": "Sofar Solar",
        "SOLAR N PLUS": "Solar N Plus",
        "SOLFACIL": "Solfacil",
        "Sungrow": "Sungrow",
        "Sunova": "Sunova",
        "TRINA": "Trina Solar",
        "TSUNESS": "Tsuness",
        "Ucb": "UCB",
        "Unipower": "Unipower",
        "Znshine": "Znshine",
        "Ztroon": "Ztroon",
    }

    return normalization_map.get(name, name)


def main():
    json_file = Path(
        r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\unified_products.json"
    )

    print("Extraindo fabricantes...")
    manufacturers = extract_manufacturers(json_file)

    print("\n" + "=" * 80)
    print("LISTA UNIFICADA DE FABRICANTES - YSH SOLAR INVENTORY")
    print("=" * 80)

    # Normalizar e consolidar
    normalized_all = {}
    for mfg, count in manufacturers["all"].items():
        normalized = normalize_manufacturer_name(mfg)
        if normalized:
            normalized_all[normalized] = normalized_all.get(normalized, 0) + count

    # Ordenar por contagem
    sorted_manufacturers = sorted(
        normalized_all.items(), key=lambda x: x[1], reverse=True
    )

    print(f"\nTotal de Fabricantes Únicos: {len(sorted_manufacturers)}")
    print(f"Total de Componentes: {sum(normalized_all.values())}\n")

    print("-" * 80)
    print(f"{'#':<5} {'Fabricante':<30} {'Produtos':<15} {'%':<10}")
    print("-" * 80)

    total = sum(normalized_all.values())
    for idx, (mfg, count) in enumerate(sorted_manufacturers, 1):
        percentage = (count / total) * 100
        print(f"{idx:<5} {mfg:<30} {count:<15} {percentage:.1f}%")

    print("-" * 80)

    # Salvar relatório
    output = {
        "total_manufacturers": len(sorted_manufacturers),
        "total_components": total,
        "manufacturers": [
            {
                "rank": idx,
                "name": mfg,
                "product_count": count,
                "percentage": round((count / total) * 100, 2),
            }
            for idx, (mfg, count) in enumerate(sorted_manufacturers, 1)
        ],
    }

    output_file = json_file.parent / "manufacturers_unified_list.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nRelatório salvo em: {output_file}")


if __name__ == "__main__":
    main()
