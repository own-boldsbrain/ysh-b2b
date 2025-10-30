#!/usr/bin/env python3
"""
Extração de especificações técnicas dos dados brutos dos distribuidores.
Prioriza campos estruturados, depois extrai de descrições/nomes.
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

def extract_power_from_text(text: str) -> Optional[float]:
    """Extrai potência de texto (kW, kWp, W)"""
    if not text:
        return None
    
    text = text.upper()
    
    # Padrões de potência
    patterns = [
        r'(\d+[\.,]?\d*)\s*KWP',
        r'(\d+[\.,]?\d*)\s*KW(?!P)',
        r'(\d+)\s*W\b(?!P)',
        r'(\d+[\.,]?\d*)KWP',
        r'(\d+[\.,]?\d*)KW(?!P)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            power_str = match.group(1).replace(',', '.')
            power = float(power_str)
            
            # Converter W para kW
            if 'W' in match.group(0) and 'KW' not in match.group(0):
                power = power / 1000
            
            # Validar range razoável (0.1kW - 500kW)
            if 0.1 <= power <= 500:
                return power
    
    return None

def extract_voltage_from_text(text: str) -> Optional[int]:
    """Extrai tensão de texto (V, Vac, Vdc)"""
    if not text:
        return None
    
    text = text.upper()
    
    # Padrões comuns: 220V, 380V, 110V, etc.
    patterns = [
        r'(\d{2,3})\s*V(?:AC|DC)?',
        r'(\d{2,3})V',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Pegar a tensão mais comum ou a primeira
            voltages = [int(v) for v in matches if 100 <= int(v) <= 1000]
            if voltages:
                return voltages[0]
    
    return None

def extract_efficiency_from_text(text: str) -> Optional[float]:
    """Extrai eficiência de texto (%EF, % Ef., Eficiência)"""
    if not text:
        return None
    
    text = text.upper()
    
    # Padrões: "22,1% EF", "98.5% Efficiency"
    patterns = [
        r'(\d+[\.,]?\d*)\s*%\s*EF',
        r'EFICI[ÊE]NCIA[:\s]*(\d+[\.,]?\d*)\s*%',
        r'(\d+[\.,]?\d*)\s*%(?:\s*DE)?\s*EFICI',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            eff_str = match.group(1).replace(',', '.')
            eff = float(eff_str)
            
            # Validar range razoável (50-99.9%)
            if 50 <= eff <= 99.9:
                return eff
    
    return None

def extract_mppt_count_from_text(text: str) -> Optional[int]:
    """Extrai número de MPPTs de texto"""
    if not text:
        return None
    
    text = text.upper()
    
    # Padrões: "2 MPPT", "MPPT: 6", etc.
    patterns = [
        r'(\d+)\s*MPPT',
        r'MPPT[S]?\s*[:\-]?\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            mppt_count = int(match.group(1))
            if 1 <= mppt_count <= 20:
                return mppt_count
    
    return None

def process_fotus_products() -> List[Dict[str, Any]]:
    """Processa produtos do FOTUS e extrai specs"""
    
    fotus_file = Path(__file__).parent / "data" / "products-inventory" / "distributors" / "fotus" / "fotus-kits.csv"
    
    print(f"📂 Carregando FOTUS: {fotus_file}")
    
    with open(fotus_file, encoding='utf-8') as f:
        fotus_data = json.load(f)
    
    print(f"✅ Total produtos FOTUS: {len(fotus_data)}")
    
    enriched = []
    stats = {"power": 0, "voltage": 0, "efficiency": 0, "mppt": 0}
    
    for product in fotus_data:
        sku = product.get('id', '').replace('FOTUS-', 'FOTUS').replace('-', '')
        name = product.get('name', '')
        
        # Priorizar campos estruturados
        power_kwp = product.get('potencia_kwp')
        if not power_kwp:
            power_kwp = extract_power_from_text(name)
        
        # Extrair de texto
        voltage_v = extract_voltage_from_text(name)
        efficiency = extract_efficiency_from_text(name)
        mppt_count = extract_mppt_count_from_text(name)
        
        # Inferir tipo de equipamento
        equipment_type = "kit_completo"
        if "MICROINVERSOR" in name.upper():
            equipment_type = "microinversor"
        elif "INVERSOR" in name.upper():
            equipment_type = "inversor"
        
        # Extrair fabricante
        manufacturer = "UNKNOWN"
        if "DEYE" in name.upper():
            manufacturer = "DEYE"
        elif "GROWATT" in name.upper():
            manufacturer = "GROWATT"
        elif "GOODWE" in name.upper():
            manufacturer = "GOODWE"
        elif "SOLAR N PLUS" in name.upper():
            manufacturer = "SOLAR N PLUS"
        
        enriched_product = {
            "sku": sku,
            "original_id": product.get('id'),
            "name": name,
            "manufacturer": manufacturer,
            "equipment_type": equipment_type,
            "distributor": "FOTUS",
            "price_brl": product.get('price_brl'),
            "specs": {
                "power_kwp": power_kwp,
                "voltage_v": voltage_v,
                "efficiency_percent": efficiency,
                "mppt_count": mppt_count,
            },
            "components": {
                "panels": product.get('panels', []),
                "inverters": product.get('inverters', []),
                "batteries": product.get('batteries', []),
            }
        }
        
        # Contagem de estatísticas
        if power_kwp:
            stats["power"] += 1
        if voltage_v:
            stats["voltage"] += 1
        if efficiency:
            stats["efficiency"] += 1
        if mppt_count:
            stats["mppt"] += 1
        
        enriched.append(enriched_product)
    
    # Exibir estatísticas
    total = len(enriched)
    print(f"\n📊 Estatísticas de Extração:")
    print(f"  Power:      {stats['power']:4d}/{total} ({stats['power']/total*100:5.1f}%)")
    print(f"  Voltage:    {stats['voltage']:4d}/{total} ({stats['voltage']/total*100:5.1f}%)")
    print(f"  Efficiency: {stats['efficiency']:4d}/{total} ({stats['efficiency']/total*100:5.1f}%)")
    print(f"  MPPT Count: {stats['mppt']:4d}/{total} ({stats['mppt']/total*100:5.1f}%)")
    
    # Exibir primeiros 5 exemplos
    print(f"\n🔍 Primeiros 5 produtos enriquecidos:")
    for i, prod in enumerate(enriched[:5], 1):
        print(f"\n  {i}. SKU: {prod['sku']}")
        print(f"     Nome: {prod['name'][:60]}...")
        print(f"     Specs: Power={prod['specs']['power_kwp']}kWp | Voltage={prod['specs']['voltage_v']}V | Eff={prod['specs']['efficiency_percent']}% | MPPT={prod['specs']['mppt_count']}")
    
    return enriched

def main():
    """Função principal"""
    print("=" * 80)
    print("🔧 Extração de Especificações Técnicas dos Dados Brutos")
    print("=" * 80)
    
    # Processar FOTUS
    fotus_enriched = process_fotus_products()
    
    # Salvar resultado
    output_file = Path(__file__).parent / "fotus-specs-extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fotus_enriched, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Arquivo salvo: {output_file}")
    print(f"   Total de produtos: {len(fotus_enriched)}")

if __name__ == "__main__":
    main()
