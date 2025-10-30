"""
Utilitário para Análise (Parsing) de SKUs da YSH Solar.

Este módulo contém a lógica para decompor um SKU da YSH em seus
componentes fundamentais, como fabricante, modelo, potência e tecnologia.
"""

import re


def parse_sku(sku: str) -> dict:
    """
    Analisa um SKU de painel ou inversor e retorna um dicionário com seus componentes.

    Exemplos de SKU de Painel:
    - PNL-JINKO-TGR-585W-NTYPE
    - PNL-LONGI-HMO6-665W-BF

    Exemplos de SKU de Inversor (padrão a ser definido):
    - INV-GROWATT-MIN-5000TL-XH
    - INV-DEYE-SUN-8K-SG04LP3-EU

    Args:
        sku (str): O SKU do produto.

    Returns:
        dict: Um dicionário contendo as partes do SKU.
    """
    sku_info = {"original_sku": sku, "type": "unknown"}

    # Padrão para Painéis (PNL)
    panel_pattern = re.compile(
        r"PNL"
        r"-(?P<manufacturer>[A-Z0-9]+)"  # Fabricante (ex: JINKO)
        r"-(?P<series>[A-Z0-9]+)"  # Série/Modelo (ex: TGR)
        r"-(?P<power>\d+)W"  # Potência (ex: 585W)
        r"(-(?P<tech>[A-Z0-9\-\_]+))?",  # Tecnologia (opcional, ex: NTYPE, BF)
        re.IGNORECASE,
    )

    # Padrão para Inversores (INV)
    inverter_pattern = re.compile(
        r"INV"
        r"-(?P<manufacturer>[A-Z0-9]+)"  # Fabricante (ex: GROWATT)
        r"-(?P<model>.+)",  # O resto é considerado modelo
        re.IGNORECASE,
    )

    match = panel_pattern.match(sku)
    if match:
        data = match.groupdict()
        sku_info.update(
            {
                "type": "Panel",
                "manufacturer": data.get("manufacturer"),
                "series": data.get("series"),
                "power_watts": int(data.get("power")),
                "technology": data.get("tech"),
            }
        )
        # Queries de busca múltiplas para melhor cobertura
        base_query = (
            f"{data.get('manufacturer')} {data.get('series')} {data.get('power')}W"
        )
        sku_info["search_query"] = base_query
        sku_info["search_queries"] = [
            base_query,  # Query base
            f"{base_query} {data.get('tech') or ''}".strip(),  # Com tecnologia
            f"{data.get('manufacturer')} {data.get('series')} datasheet",  # Foco em datasheet
            f"{data.get('manufacturer')} {data.get('series')} specifications",  # Foco em specs
        ]
        return sku_info

    match = inverter_pattern.match(sku)
    if match:
        data = match.groupdict()
        model_full = data.get("model")

        # Tenta extrair uma série/modelo mais limpo
        model_parts = model_full.split("-")
        series = model_parts[0] if model_parts else ""

        sku_info.update(
            {
                "type": "Inverter",
                "manufacturer": data.get("manufacturer"),
                "model": model_full,
                "series": series,
            }
        )
        # Queries de busca múltiplas para melhor cobertura
        base_query = f"{data.get('manufacturer')} {model_full.replace('-', ' ')}"
        sku_info["search_query"] = base_query
        sku_info["search_queries"] = [
            base_query,  # Query base
            f"{data.get('manufacturer')} {series}",  # Só fabricante e série
            f"{base_query} datasheet",  # Foco em datasheet
            f"{base_query} manual",  # Foco em manual
        ]
        return sku_info

    # Se nenhum padrão corresponder, retorna o tipo como 'unknown'
    return sku_info


# Exemplo de uso
if __name__ == "__main__":
    skus_to_test = [
        "PNL-JINKO-TGR-585W-NTYPE",
        "PNL-LONGI-HMO6-665W-BF",
        "PNL-TRINA-VERTEX-670W-MONO",
        "INV-GROWATT-MIN-5000TL-XH",
        "INV-DEYE-SUN-8K-SG04LP3-EU",
        "UNKNOWN-SKU-FORMAT",
    ]

    for sku in skus_to_test:
        parsed = parse_sku(sku)
        print(f"SKU: {sku}\nParsed: {parsed}\n")
