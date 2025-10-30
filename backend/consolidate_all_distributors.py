#!/usr/bin/env python3
"""
Consolidação de dados de todos os distribuidores para Digital Twin.
Gera SKUs padronizados e extrai especificações técnicas completas.
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

def normalize_sku(text: str, distributor: str, product_type: str = "KITS") -> str:
    """Gera SKU padronizado: DISTRIBUITORTIPO{specs}"""
    if not text:
        return f"{distributor.upper()}{product_type}UNKNOWN"
    
    # Remover caracteres especiais e normalizar
    sku = text.upper()
    sku = sku.replace(' ', '').replace('-', '').replace('_', '')
    sku = sku.replace('/', '').replace('|', '').replace('.', '')
    sku = sku.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    
    # Limitar tamanho
    if len(sku) > 50:
        sku = sku[:50]
    
    return sku

def extract_power_kwp(product: Dict[str, Any]) -> Optional[float]:
    """Extrai potência em kWp"""
    # Priorizar campo estruturado
    for field in ['potencia_kwp', 'system_power_kwp', 'power_kwp']:
        if field in product and product[field]:
            return float(product[field])
    
    # Extrair de nome/título
    text = str(product.get('name', '') or product.get('title', ''))
    if not text:
        return None
    
    text = text.upper()
    patterns = [
        r'(\d+[\.,]?\d*)\s*KWP',
        r'(\d+[\.,]?\d*)KWP',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            power_str = match.group(1).replace(',', '.')
            power = float(power_str)
            if 0.1 <= power <= 500:
                return power
    
    return None

def extract_voltage_v(product: Dict[str, Any]) -> Optional[int]:
    """Extrai tensão em V"""
    text = str(product.get('name', '') or product.get('title', ''))
    if not text:
        return None
    
    text = text.upper()
    patterns = [
        r'(\d{3})\s*V(?:AC|DC)?',  # 220V, 380V
        r'/(\d{3})V',  # 48/220V
        r'-(\d{3})V',  # 48-220V
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            voltages = [int(v) for v in matches if 100 <= int(v) <= 1000]
            if voltages:
                return voltages[0]
    
    return None

def extract_manufacturer(product: Dict[str, Any]) -> str:
    """Extrai fabricante"""
    # Verificar campo direto
    if 'manufacturer' in product and product['manufacturer']:
        return str(product['manufacturer']).upper()
    
    # Extrair de componentes (painéis, inversores)
    if 'panels' in product and product['panels']:
        panels = product['panels']
        if isinstance(panels, list) and len(panels) > 0:
            if 'brand' in panels[0] and panels[0]['brand']:
                return str(panels[0]['brand']).upper()
    
    if 'inverters' in product and product['inverters']:
        inverters = product['inverters']
        if isinstance(inverters, list) and len(inverters) > 0:
            if 'brand' in inverters[0] and inverters[0]['brand']:
                return str(inverters[0]['brand']).upper()
    
    # Extrair de nome
    text = str(product.get('name', ''))
    brands = [
        'DEYE', 'GROWATT', 'GOODWE', 'HUAWEI', 'SUNGROW', 'FRONIUS',
        'SAJ', 'ENPHASE', 'HOYMILES', 'ASTRONERGY', 'CANADIAN SOLAR',
        'TRINA', 'JINKO', 'JA SOLAR', 'LONGI', 'RISEN', 'SOLAR N PLUS'
    ]
    
    for brand in brands:
        if brand in text.upper():
            return brand
    
    return "UNKNOWN"

def extract_equipment_type(product: Dict[str, Any]) -> str:
    """Determina tipo de equipamento"""
    text = str(product.get('name', '') or product.get('title', '') or product.get('type', '')).upper()
    
    if 'KIT' in text or 'KP' in text:
        return 'kit_completo'
    elif 'MICROINVERSOR' in text or 'MICRO-INVERSOR' in text:
        return 'microinversor'
    elif 'INVERSOR' in text or 'INVERTER' in text:
        return 'inversor'
    elif 'PAINEL' in text or 'PANEL' in text or 'MÓDULO' in text:
        return 'painel'
    elif 'BATERIA' in text or 'BATTERY' in text:
        return 'bateria'
    elif 'ESTRUTURA' in text or 'STRUCTURE' in text:
        return 'estrutura'
    
    return 'outro'

def consolidate_distributor(dist_name: str, files: List[Path]) -> List[Dict[str, Any]]:
    """Consolida produtos de um distribuidor"""
    
    products = []
    
    for file_path in files:
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                continue
            
            for item in data:
                # Gerar SKU normalizado
                original_id = item.get('id', item.get('sku', ''))
                equipment_type = extract_equipment_type(item)
                sku = normalize_sku(original_id, dist_name, equipment_type[:4].upper())
                
                # Extrair specs
                power_kwp = extract_power_kwp(item)
                voltage_v = extract_voltage_v(item)
                manufacturer = extract_manufacturer(item)
                
                # Montar produto consolidado
                product = {
                    "sku": sku,
                    "original_id": original_id,
                    "distributor": dist_name.upper(),
                    "equipment_type": equipment_type,
                    "manufacturer": manufacturer,
                    "name": item.get('name', item.get('title', '')),
                    "price_brl": item.get('price_brl', item.get('price', 0)),
                    "specs": {
                        "power_kwp": power_kwp,
                        "voltage_v": voltage_v,
                    },
                    "components": {
                        "panels": item.get('panels', []),
                        "inverters": item.get('inverters', []),
                        "batteries": item.get('batteries', []),
                    },
                    "image_url": item.get('image_url', ''),
                    "source_file": file_path.name,
                    "consolidated_at": datetime.utcnow().isoformat() + "Z"
                }
                
                products.append(product)
        
        except Exception as e:
            print(f"  ⚠️  Erro ao processar {file_path.name}: {str(e)[:50]}")
    
    return products

def main():
    """Função principal"""
    
    print("=" * 80)
    print("🔄 Consolidação de Dados de Distribuidores para Digital Twin")
    print("=" * 80)
    
    dist_base = Path(__file__).parent / "data" / "products-inventory" / "distributors"
    
    all_products = []
    
    # FOTUS
    print("\n📂 Processando FOTUS...")
    fotus_path = dist_base / "fotus"
    fotus_files = [
        fotus_path / "fotus-kits.csv",
        # Adicionar outros arquivos conforme necessário
    ]
    fotus_files = [f for f in fotus_files if f.exists()]
    fotus_products = consolidate_distributor("FOTUS", fotus_files)
    all_products.extend(fotus_products)
    print(f"  ✅ {len(fotus_products)} produtos processados")
    
    # NEOSOLAR
    print("\n📂 Processando NEOSOLAR...")
    neosolar_path = dist_base / "neosolar"
    neosolar_files = [
        neosolar_path / "neosolar-kits-with-skus.json",
    ]
    neosolar_files = [f for f in neosolar_files if f.exists()]
    neosolar_products = consolidate_distributor("NEOSOLAR", neosolar_files)
    all_products.extend(neosolar_products)
    print(f"  ✅ {len(neosolar_products)} produtos processados")
    
    # FORTLEV
    print("\n📂 Processando FORTLEV...")
    fortlev_path = dist_base / "fortlev"
    fortlev_files = [
        fortlev_path / "fortlev-kits-with-skus.json",
        fortlev_path / "fortlev-inverters.json",
    ]
    fortlev_files = [f for f in fortlev_files if f.exists()]
    fortlev_products = consolidate_distributor("FORTLEV", fortlev_files)
    all_products.extend(fortlev_products)
    print(f"  ✅ {len(fortlev_products)} produtos processados")
    
    # ODEX
    print("\n📂 Processando ODEX...")
    odex_path = dist_base / "odex"
    odex_files = [
        odex_path / "odex-inverters.json",
        odex_path / "odex-panels.json",
    ]
    odex_files = [f for f in odex_files if f.exists()]
    odex_products = consolidate_distributor("ODEX", odex_files)
    all_products.extend(odex_products)
    print(f"  ✅ {len(odex_products)} produtos processados")
    
    # SOLFACIL
    print("\n📂 Processando SOLFACIL...")
    solfacil_path = dist_base / "solfacil"
    solfacil_files = [
        solfacil_path / "solfacil-inverters.json",
        solfacil_path / "solfacil-panels.json",
    ]
    solfacil_files = [f for f in solfacil_files if f.exists()]
    solfacil_products = consolidate_distributor("SOLFACIL", solfacil_files)
    all_products.extend(solfacil_products)
    print(f"  ✅ {len(solfacil_products)} produtos processados")
    
    # Estatísticas
    print(f"\n{'='*80}")
    print(f"📊 ESTATÍSTICAS DE CONSOLIDAÇÃO")
    print(f"{'='*80}")
    
    print(f"\nTotal de produtos: {len(all_products)}")
    
    # Por distribuidor
    by_dist = {}
    for p in all_products:
        dist = p['distributor']
        by_dist[dist] = by_dist.get(dist, 0) + 1
    
    print(f"\nPor Distribuidor:")
    for dist, count in sorted(by_dist.items()):
        print(f"  {dist:15s}: {count:5d}")
    
    # Por tipo
    by_type = {}
    for p in all_products:
        eq_type = p['equipment_type']
        by_type[eq_type] = by_type.get(eq_type, 0) + 1
    
    print(f"\nPor Tipo de Equipamento:")
    for eq_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {eq_type:20s}: {count:5d}")
    
    # Cobertura de specs
    with_power = sum(1 for p in all_products if p['specs']['power_kwp'])
    with_voltage = sum(1 for p in all_products if p['specs']['voltage_v'])
    
    total = len(all_products)
    print(f"\nCobertura de Especificações:")
    print(f"  Power (kWp):  {with_power:5d}/{total} ({with_power/total*100:5.1f}%)")
    print(f"  Voltage (V):  {with_voltage:5d}/{total} ({with_voltage/total*100:5.1f}%)")
    
    # Salvar resultado
    output_file = Path(__file__).parent / "consolidated-products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Arquivo salvo: {output_file}")
    print(f"   Tamanho: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Primeiros 3 exemplos
    print(f"\n📦 Primeiros 3 Produtos:")
    for i, p in enumerate(all_products[:3], 1):
        print(f"\n  {i}. {p['sku']}")
        print(f"     Nome: {p['name'][:60]}")
        print(f"     Distribuidor: {p['distributor']}")
        print(f"     Tipo: {p['equipment_type']}")
        print(f"     Power: {p['specs']['power_kwp']}kWp | Voltage: {p['specs']['voltage_v']}V")
        print(f"     Preço: R$ {p['price_brl']:.2f}")

if __name__ == "__main__":
    main()
