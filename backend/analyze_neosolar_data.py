#!/usr/bin/env python3
"""
Análise exploratória dos dados da Neosolar para entender estrutura e campos disponíveis.
"""
import json
from pathlib import Path

def analyze_neosolar_data():
    """Analisa o arquivo neosolar-kits-with-skus.json"""
    
    file_path = Path(__file__).parent / "data" / "products-inventory" / "distributors" / "neosolar" / "neosolar-kits-with-skus.json"
    
    print(f"📂 Carregando: {file_path}")
    
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    
    # Informações gerais
    print(f"\n✅ Total de produtos: {len(data)}")
    print(f"📊 Tipo de estrutura: {'lista' if isinstance(data, list) else 'dicionário'}")
    
    # Amostra
    sample = data[0] if isinstance(data, list) else list(data.values())[0]
    
    print(f"\n🔑 Campos disponíveis ({len(sample.keys())} campos):")
    for i, key in enumerate(sample.keys(), 1):
        value = sample[key]
        value_type = type(value).__name__
        value_preview = str(value)[:50] if value else "null"
        print(f"  {i:2d}. {key:30s} ({value_type:10s}) = {value_preview}")
    
    print(f"\n📦 Primeiro produto completo:")
    print(json.dumps(sample, indent=2, ensure_ascii=False)[:3000])
    print("\n... (conteúdo truncado para exibição)")
    
    # Análise de campos técnicos
    print(f"\n🔧 Análise de campos técnicos:")
    
    # Procurar por campos de potência
    power_fields = [k for k in sample.keys() if any(word in k.lower() for word in ['power', 'potencia', 'potência', 'watt', 'kw'])]
    if power_fields:
        print(f"  ⚡ Campos de potência encontrados: {power_fields}")
        for field in power_fields:
            print(f"     → {field}: {sample[field]}")
    
    # Procurar por campos de tensão
    voltage_fields = [k for k in sample.keys() if any(word in k.lower() for word in ['voltage', 'tensao', 'tensão', 'volt', 'v'])]
    if voltage_fields:
        print(f"  🔌 Campos de tensão encontrados: {voltage_fields}")
        for field in voltage_fields:
            print(f"     → {field}: {sample[field]}")
    
    # Procurar por campos de eficiência
    efficiency_fields = [k for k in sample.keys() if any(word in k.lower() for word in ['efficiency', 'eficiencia', 'eficiência', 'rendimento'])]
    if efficiency_fields:
        print(f"  📈 Campos de eficiência encontrados: {efficiency_fields}")
        for field in efficiency_fields:
            print(f"     → {field}: {sample[field]}")
    
    # Procurar por SKU
    sku_fields = [k for k in sample.keys() if 'sku' in k.lower()]
    if sku_fields:
        print(f"  🏷️  Campos de SKU encontrados: {sku_fields}")
        for field in sku_fields:
            print(f"     → {field}: {sample[field]}")
    
    # Contar quantos produtos têm SKU
    if isinstance(data, list):
        products_with_sku = sum(1 for item in data if any(item.get(field) for field in sku_fields))
        print(f"\n📊 Produtos com SKU: {products_with_sku}/{len(data)} ({products_with_sku/len(data)*100:.1f}%)")

if __name__ == "__main__":
    analyze_neosolar_data()
