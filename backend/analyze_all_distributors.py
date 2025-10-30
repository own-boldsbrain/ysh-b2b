#!/usr/bin/env python3
"""
Análise completa de todos os distribuidores para mapear campos disponíveis.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

def analyze_distributor_files(dist_name: str, dist_path: Path) -> Dict[str, Any]:
    """Analisa arquivos de um distribuidor"""
    
    result = {
        "name": dist_name,
        "files": [],
        "total_products": 0,
        "sample_fields": set(),
        "sample_product": None
    }
    
    # Procurar arquivos JSON relevantes
    json_files = []
    for pattern in ["*kits*.json", "*inverter*.json", "*panel*.json", "*-kits.csv"]:
        json_files.extend(dist_path.glob(pattern))
    
    # Filtrar arquivos de schema/mapping
    json_files = [f for f in json_files if not any(x in f.name.lower() for x in ['schema', 'mapping', 'uuid', 'backup'])]
    
    for file_path in json_files:
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                count = len(data)
                result["total_products"] += count
                result["files"].append({
                    "name": file_path.name,
                    "count": count,
                    "type": "list"
                })
                
                # Coletar campos do primeiro produto
                if data and not result["sample_product"]:
                    result["sample_product"] = data[0]
                    result["sample_fields"] = set(data[0].keys())
        except Exception as e:
            pass
    
    return result

def main():
    """Análise de todos os distribuidores"""
    
    print("=" * 80)
    print("📊 Análise Completa de Distribuidores")
    print("=" * 80)
    
    dist_base = Path(__file__).parent / "data" / "products-inventory" / "distributors"
    
    distributors = ["fotus", "neosolar", "odex", "meugerador", "solfacil", "fortlev"]
    
    all_results = {}
    
    for dist_name in distributors:
        dist_path = dist_base / dist_name
        if not dist_path.exists():
            print(f"\n⚠️  {dist_name}: Diretório não encontrado")
            continue
        
        print(f"\n{'='*80}")
        print(f"📂 {dist_name.upper()}")
        print(f"{'='*80}")
        
        result = analyze_distributor_files(dist_name, dist_path)
        all_results[dist_name] = result
        
        print(f"\nTotal de produtos: {result['total_products']}")
        print(f"Arquivos encontrados: {len(result['files'])}")
        
        for file_info in result['files']:
            print(f"  • {file_info['name']:50s} ({file_info['count']:4d} produtos)")
        
        if result['sample_fields']:
            print(f"\nCampos disponíveis ({len(result['sample_fields'])} campos):")
            
            # Categorizar campos
            tech_fields = [f for f in result['sample_fields'] if any(
                x in f.lower() for x in ['power', 'voltage', 'efficiency', 'mppt', 'panel', 'inverter', 'battery', 'potencia', 'tensao']
            )]
            
            pricing_fields = [f for f in result['sample_fields'] if any(
                x in f.lower() for x in ['price', 'cost', 'pricing']
            )]
            
            id_fields = [f for f in result['sample_fields'] if any(
                x in f.lower() for x in ['id', 'sku', 'name', 'title']
            )]
            
            if id_fields:
                print(f"  🏷️  Identificação: {', '.join(sorted(id_fields))}")
            if tech_fields:
                print(f"  ⚡ Técnicos: {', '.join(sorted(tech_fields)[:10])}")
            if pricing_fields:
                print(f"  💰 Pricing: {', '.join(sorted(pricing_fields))}")
            
        # Exibir produto de exemplo
        if result['sample_product']:
            print(f"\n📦 Produto de Exemplo:")
            sample = result['sample_product']
            
            # Mostrar campos mais relevantes
            for key in ['id', 'sku', 'name', 'title', 'potencia_kwp', 'power_kw', 'price_brl']:
                if key in sample:
                    value = str(sample[key])[:60]
                    print(f"  {key:20s} = {value}")
    
    # Resumo consolidado
    print(f"\n{'='*80}")
    print(f"📊 RESUMO CONSOLIDADO")
    print(f"{'='*80}")
    
    total_products = sum(r['total_products'] for r in all_results.values())
    print(f"\nTotal de Produtos: {total_products}")
    
    for dist_name, result in all_results.items():
        percent = (result['total_products'] / total_products * 100) if total_products > 0 else 0
        print(f"  {dist_name:15s}: {result['total_products']:5d} ({percent:5.1f}%)")
    
    # Identificar campos comuns
    print(f"\n🔑 Campos Comuns Entre Distribuidores:")
    
    common_fields = None
    for result in all_results.values():
        if result['sample_fields']:
            if common_fields is None:
                common_fields = result['sample_fields'].copy()
            else:
                common_fields = common_fields.intersection(result['sample_fields'])
    
    if common_fields:
        print(f"  {', '.join(sorted(common_fields)[:15])}")
    else:
        print("  Nenhum campo comum encontrado")
    
    # Salvar resultado detalhado
    output_file = Path(__file__).parent / "distributors-analysis.json"
    
    # Converter sets para listas para serialização JSON
    for result in all_results.values():
        if 'sample_fields' in result:
            result['sample_fields'] = sorted(result['sample_fields'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Análise salva em: {output_file}")

if __name__ == "__main__":
    main()
