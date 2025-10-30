#!/usr/bin/env python3
"""
Análise dos SKUs do FOTUS para comparar com Digital Twin SKUs.
"""
import json
from pathlib import Path

def analyze_fotus_skus():
    """Analisa os SKUs do FOTUS e compara com Digital Twin"""
    
    # Carregar dados FOTUS
    fotus_path = Path(__file__).parent / "data" / "products-inventory" / "distributors" / "fotus" / "fotus-kits-with-skus.json"
    
    print(f"📂 Carregando FOTUS: {fotus_path}")
    
    with open(fotus_path, encoding='utf-8') as f:
        fotus_data = json.load(f)
    
    print(f"\n✅ Total produtos FOTUS: {len(fotus_data)}")
    
    # Mostrar primeiros SKUs
    print(f"\n🏷️  Primeiros 10 SKUs FOTUS:")
    for i, kit in enumerate(fotus_data[:10], 1):
        sku = kit.get('sku', 'NO_SKU')
        name = kit.get('name', 'NO_NAME')
        power = kit.get('potencia_kwp', 0)
        print(f"  {i:2d}. SKU: {sku:40s} | Power: {power:6.2f}kWp | Name: {name[:50]}")
    
    # Exemplos de Digital Twin SKUs
    print(f"\n📦 Exemplos de Digital Twin SKUs:")
    digital_twin_examples = [
        "FOTUSKP021704KWPCERAMICOKITS",
        "FOTUSKP020804KWPCERAMICOKITS",
        "FOTUSKP021304KWPCERAMICOKITS",
        "FOTUSKP020602KWPFIBROCIMENTOKITS",
        "GROWATTINV8000MTL"
    ]
    
    for i, sku in enumerate(digital_twin_examples, 1):
        print(f"  {i}. {sku}")
    
    # Verificar se há padrões correspondentes
    print(f"\n🔍 Analisando padrões de SKU...")
    
    # Padrão 1: SKUs que começam com FOTUS
    fotus_skus = [kit.get('sku', '') for kit in fotus_data if kit.get('sku', '').startswith('FOTUS')]
    print(f"  ✅ SKUs começando com 'FOTUS': {len(fotus_skus)}")
    if fotus_skus:
        print(f"     Exemplos: {fotus_skus[:3]}")
    
    # Padrão 2: SKUs com KP (Kit Fotovoltaico)
    kp_skus = [kit.get('sku', '') for kit in fotus_data if 'KP' in kit.get('sku', '')]
    print(f"  ✅ SKUs contendo 'KP': {len(kp_skus)}")
    if kp_skus:
        print(f"     Exemplos: {kp_skus[:3]}")
    
    # Padrão 3: SKUs com CERAMIC ou FIBROCIMENTO
    material_skus = [kit.get('sku', '') for kit in fotus_data if any(mat in kit.get('sku', '') for mat in ['CERAMIC', 'FIBRO'])]
    print(f"  ✅ SKUs com materiais (CERAMIC/FIBRO): {len(material_skus)}")
    if material_skus:
        print(f"     Exemplos: {material_skus[:3]}")
    
    # Verificar se há SKUs exatamente como os do Digital Twin
    print(f"\n🎯 Verificando match exato com Digital Twin SKUs...")
    exact_matches = 0
    for dt_sku in digital_twin_examples:
        for kit in fotus_data:
            if kit.get('sku', '') == dt_sku:
                exact_matches += 1
                print(f"  ✅ MATCH ENCONTRADO: {dt_sku}")
                print(f"     Nome: {kit.get('name', 'N/A')}")
                print(f"     Potência: {kit.get('potencia_kwp', 0)}kWp")
                break
    
    if exact_matches == 0:
        print(f"  ❌ Nenhum match exato encontrado")
        print(f"\n💡 Possíveis razões:")
        print(f"     1. SKUs do Digital Twin podem vir de outro distribuidor")
        print(f"     2. SKUs do Digital Twin podem ser códigos internos YSH")
        print(f"     3. Mapeamento pode estar em outro arquivo (consolidate_inventory.py)")
    
    # Analisar campos disponíveis
    print(f"\n📊 Campos disponíveis no primeiro produto FOTUS:")
    if fotus_data:
        sample = fotus_data[0]
        for key in sorted(sample.keys()):
            value = sample[key]
            print(f"  • {key:30s} = {str(value)[:60]}")

if __name__ == "__main__":
    analyze_fotus_skus()
