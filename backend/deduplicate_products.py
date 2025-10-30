#!/usr/bin/env python3
"""
Deduplicação Inteligente de Produtos - Cria SKUs únicos com informações consolidadas
"""
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Any, Optional

def normalize_text(text: str) -> str:
    """Normaliza texto para comparação"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.upper().strip())

def extract_power_from_name(name: str) -> Optional[float]:
    """Extrai potência do nome do produto"""
    patterns = [
        r'(\d+(?:[.,]\d+)?)\s*KWP?',
        r'(\d+(?:[.,]\d+)?)KW',
        r'(\d+(?:[.,]\d+)?)WP',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, name.upper())
        if matches:
            for match in matches:
                power = float(match.replace(',', '.'))
                if 0.1 <= power <= 1000:
                    return power
    return None

def calculate_similarity_score(prod1: Dict, prod2: Dict) -> float:
    """Calcula score de similaridade entre dois produtos"""
    score = 0.0
    total_weight = 0.0

    # Potência (peso alto)
    p1_power = prod1['specs']['power_kwp']
    p2_power = prod2['specs']['power_kwp']
    if p1_power and p2_power:
        if abs(p1_power - p2_power) < 0.1:  # Mesma potência
            score += 1.0
        elif abs(p1_power - p2_power) / max(p1_power, p2_power) < 0.05:  # Diferença < 5%
            score += 0.8
        total_weight += 1.0

    # Fabricante (peso alto)
    p1_manuf = normalize_text(prod1['manufacturer'])
    p2_manuf = normalize_text(prod2['manufacturer'])
    if p1_manuf and p2_manuf:
        if p1_manuf == p2_manuf:
            score += 1.0
        elif p1_manuf in p2_manuf or p2_manuf in p1_manuf:
            score += 0.7
        total_weight += 1.0

    # Tipo de equipamento (peso médio)
    if prod1['equipment_type'] == prod2['equipment_type']:
        score += 0.8
        total_weight += 0.8

    # Componentes similares (peso médio)
    p1_panels = len(prod1['components']['panels'])
    p2_panels = len(prod2['components']['panels'])
    p1_inverters = len(prod1['components']['inverters'])
    p2_inverters = len(prod2['components']['inverters'])

    if abs(p1_panels - p2_panels) <= 1 and abs(p1_inverters - p2_inverters) <= 1:
        score += 0.6
        total_weight += 0.6

    # Nome similar (peso baixo)
    p1_name = normalize_text(prod1['name'])
    p2_name = normalize_text(prod2['name'])
    if p1_name and p2_name:
        # Calcular similaridade de strings simples
        common_words = set(p1_name.split()) & set(p2_name.split())
        if len(common_words) > 2:
            score += 0.4
            total_weight += 0.4

    return score / total_weight if total_weight > 0 else 0.0

def group_similar_products(products: List[Dict]) -> List[List[Dict]]:
    """Agrupa produtos similares usando clustering inteligente"""
    groups = []

    for product in products:
        # Tentar adicionar a um grupo existente
        added = False
        for group in groups:
            # Verificar similaridade com o primeiro produto do grupo
            if calculate_similarity_score(product, group[0]) > 0.7:
                group.append(product)
                added = True
                break

        # Se não encontrou grupo similar, criar novo
        if not added:
            groups.append([product])

    return groups

def consolidate_product_group(products: List[Dict]) -> Dict:
    """Consolida informações de um grupo de produtos similares"""

    # Produto base (o mais completo)
    base_product = max(products, key=lambda p: (
        p['specs']['power_kwp'] is not None,
        len(p['components']['panels']),
        len(p['components']['inverters']),
        p['image_url'] is not None
    ))

    # SKU único baseado nas características principais
    manufacturer = base_product['manufacturer'] or "UNKNOWN"
    power = base_product['specs']['power_kwp']
    eq_type = base_product['equipment_type']

    if power:
        power_str = f"{power:.1f}".replace('.0', '').replace('.', 'P')
        sku = f"{manufacturer.upper()[:3]}{power_str}KW{eq_type[:3].upper()}"
    else:
        sku = f"{manufacturer.upper()[:3]}UNK{eq_type[:3].upper()}"

    # Remover caracteres especiais do SKU
    sku = re.sub(r'[^A-Z0-9]', '', sku)

    # Consolidar informações de distribuidores
    distributors = {}
    all_prices = []
    all_images = []

    for product in products:
        dist = product['distributor']
        if dist not in distributors:
            distributors[dist] = {
                'count': 0,
                'prices': [],
                'original_ids': [],
                'source_files': []
            }

        distributors[dist]['count'] += 1
        distributors[dist]['original_ids'].append(product['original_id'])
        distributors[dist]['source_files'].append(product['source_file'])

        if product['price_brl']:
            try:
                price = float(str(product['price_brl']).replace(',', '.'))
                distributors[dist]['prices'].append(price)
                all_prices.append(price)
            except:
                pass

        if product['image_url']:
            all_images.append(product['image_url'])

    # Estatísticas de preços por distribuidor
    for dist_data in distributors.values():
        if dist_data['prices']:
            dist_data['price_stats'] = {
                'min': min(dist_data['prices']),
                'max': max(dist_data['prices']),
                'avg': sum(dist_data['prices']) / len(dist_data['prices']),
                'count': len(dist_data['prices'])
            }
        else:
            dist_data['price_stats'] = None

    # Melhor imagem (primeira disponível)
    best_image = all_images[0] if all_images else None

    # Consolidar componentes (usar o mais completo)
    best_components = max(products, key=lambda p: (
        len(p['components']['panels']),
        len(p['components']['inverters']),
        len(p['components']['batteries'])
    ))['components']

    # Produto consolidado
    consolidated = {
        "sku": sku,
        "manufacturer": manufacturer,
        "equipment_type": eq_type,
        "name": base_product['name'],
        "description": {
            "primary": base_product['name'],
            "technical_summary": f"{manufacturer} {eq_type} {power or 'N/A'}kWp",
            "component_count": {
                "panels": len(best_components['panels']),
                "inverters": len(best_components['inverters']),
                "batteries": len(best_components['batteries'])
            }
        },
        "specs": {
            "power_kwp": power,
            "voltage_v": base_product['specs']['voltage_v'],
            "efficiency_percent": None,  # Pode ser adicionado depois
            "dimensions_cm": None,       # Pode ser adicionado depois
            "weight_kg": None           # Pode ser adicionado depois
        },
        "components": best_components,
        "distributors": distributors,
        "pricing": {
            "price_range_brl": {
                "min": min(all_prices) if all_prices else None,
                "max": max(all_prices) if all_prices else None,
                "avg": sum(all_prices) / len(all_prices) if all_prices else None
            },
            "distributor_count": len(distributors),
            "total_offers": len(products)
        },
        "media": {
            "primary_image": best_image,
            "image_count": len(all_images),
            "image_sources": list(set(all_images))
        },
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "deduplication_consolidation",
            "original_products_count": len(products),
            "data_quality_score": "high" if power and manufacturer else "medium"
        }
    }

    return consolidated

def main():
    """Função principal"""

    print("=" * 80)
    print("🔄 DEDUPLICAÇÃO INTELIGENTE DE PRODUTOS")
    print("=" * 80)

    # Carregar dados consolidados
    consolidated_file = Path(__file__).parent / "consolidated-products.json"
    print(f"📖 Carregando: {consolidated_file.name}")

    with open(consolidated_file, encoding='utf-8') as f:
        products = json.load(f)

    print(f"   Total de produtos: {len(products)}\n")

    # Filtrar produtos válidos (com potência ou fabricante)
    valid_products = [
        p for p in products
        if p['specs']['power_kwp'] or p['manufacturer'] != 'UNKNOWN'
    ]

    print(f"🔍 Produtos válidos para deduplicação: {len(valid_products)}")
    print(f"   Removidos (sem specs): {len(products) - len(valid_products)}\n")

    # Agrupar produtos similares
    print("🔗 Agrupando produtos similares...")
    product_groups = group_similar_products(valid_products)

    print(f"   Grupos identificados: {len(product_groups)}")
    print(f"   Grupos com múltiplos produtos: {sum(1 for g in product_groups if len(g) > 1)}")
    print(f"   Produtos únicos: {sum(1 for g in product_groups if len(g) == 1)}\n")

    # Consolidar cada grupo
    print("🔄 Consolidando informações...")
    consolidated_products = []

    for i, group in enumerate(product_groups, 1):
        if i % 50 == 0:
            print(f"   Processado: {i}/{len(product_groups)} grupos")

        consolidated = consolidate_product_group(group)
        consolidated_products.append(consolidated)

    # Estatísticas finais
    print(f"\n📊 RESULTADO DA DEDUPLICAÇÃO")
    print("=" * 50)

    print(f"Produtos únicos resultantes: {len(consolidated_products)}")
    print(f"Redução: {len(products)} → {len(consolidated_products)} ({len(consolidated_products)/len(products)*100:.1f}%)")

    # Distribuição por distribuidores
    dist_counts = defaultdict(int)
    for product in consolidated_products:
        dist_counts[len(product['distributors'])] += 1

    print("\nDistribuição por número de distribuidores:")
    for num_dist, count in sorted(dist_counts.items()):
        print(f"  {num_dist} distribuidor(es): {count} produtos")

    # Salvar resultado
    output_file = Path(__file__).parent / "unique-products-consolidated.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_products, f, indent=2, ensure_ascii=False)

    size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"\n✅ Arquivo salvo: {output_file}")
    print(f"   Tamanho: {size_mb:.1f} MB")

    # Amostra
    print("\n📦 Amostra de produtos únicos:")
    for i, product in enumerate(consolidated_products[:3], 1):
        print(f"\n  {i}. {product['sku']}")
        print(f"     Nome: {product['name'][:60]}...")
        print(f"     Fabricante: {product['manufacturer']}")
        print(f"     Potência: {product['specs']['power_kwp']} kWp")
        print(f"     Distribuidores: {len(product['distributors'])}")
        print(f"     Preço médio: R$ {product['pricing']['price_range_brl']['avg']:.2f}" if product['pricing']['price_range_brl']['avg'] else "     Preço: N/A")

    print(f"\n{'='*80}")
    print("✅ Deduplicação concluída com sucesso!")
    print("=" * 80)

if __name__ == "__main__":
    main()
