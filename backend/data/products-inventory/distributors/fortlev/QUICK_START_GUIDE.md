# 🚀 Guia Rápido - Como Usar as Imagens Renomeadas

## ✅ O que foi feito

- ✅ 101 imagens de inversores foram renomeadas com nomes descritivos
- ✅ Arquivo JSON com mapeamento completo foi gerado
- ✅ Especificações técnicas foram extraídas automaticamente

## 📂 Onde estão os arquivos

```
distributors/fortlev/organized_images/
├── inverters/                    # ← Imagens originais (não modificadas)
├── inverters_renamed_v2/         # ← USAR ESTAS imagens renomeadas ⭐
└── inverters_image_mapping_complete.json  # ← Dados completos
```

## 🔥 Uso Rápido

### 1. Verificar imagens renomeadas

```powershell
# Listar todas as imagens
Get-ChildItem "inverters_renamed_v2\*.png" | Select-Object Name
```

### 2. Carregar mapeamento JSON

```python
import json

with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Exemplo: Buscar produto por código
def find_by_code(code):
    for p in products:
        if code in p['image_codes']:
            return p
    return None

# Usar
produto = find_by_code('IIN00384')
print(f"Nome: {produto['name']}")
print(f"Preço: R$ {produto['price_brl']:,.2f}")
print(f"Potência: {produto['technical_specs']['power_kw']} kW")
```

### 3. Filtrar por fabricante

```python
def filtrar_por_fabricante(fabricante):
    return [p for p in products if p['manufacturer'].upper() == fabricante.upper()]

# Exemplo
huawei_products = filtrar_por_fabricante('Huawei')
print(f"Total de inversores Huawei: {len(huawei_products)}")
```

### 4. Filtrar por potência

```python
def filtrar_por_potencia(min_kw, max_kw):
    return [p for p in products 
            if 'power_kw' in p['technical_specs'] 
            and min_kw <= p['technical_specs']['power_kw'] <= max_kw]

# Exemplo: Inversores entre 5kW e 10kW
residenciais = filtrar_por_potencia(5, 10)
print(f"Total de inversores residenciais (5-10kW): {len(residenciais)}")
```

## 🎯 Exemplos Práticos

### Exemplo 1: Listar top 10 mais caros

```python
import json

with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Ordenar por preço
products_with_price = [p for p in products if p['price_brl']]
top_10 = sorted(products_with_price, key=lambda x: x['price_brl'], reverse=True)[:10]

print("TOP 10 INVERSORES MAIS CAROS\n")
for i, p in enumerate(top_10, 1):
    print(f"{i}. {p['name']}")
    print(f"   Preço: R$ {p['price_brl']:,.2f}")
    print(f"   Potência: {p['technical_specs'].get('power_kw', 'N/A')} kW")
    print(f"   Arquivo: {p['renamed_filename']}\n")
```

### Exemplo 2: Gerar catálogo HTML

```python
def gerar_catalogo_html():
    with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Catálogo de Inversores Fortlev</title>
        <style>
            .product { border: 1px solid #ccc; padding: 15px; margin: 10px; }
            .product img { max-width: 300px; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Inversores Solares</h1>
    """
    
    for p in products[:20]:  # Primeiros 20
        specs = p['technical_specs']
        html += f"""
        <div class="product">
            <h2>{p['name']}</h2>
            <img src="inverters_renamed_v2/{p['renamed_filename']}" alt="{p['name']}">
            <p><strong>Fabricante:</strong> {p['manufacturer']}</p>
            <p><strong>Potência:</strong> {specs.get('power_kw', 'N/A')} kW</p>
            <p><strong>Voltagem:</strong> {specs.get('voltage_v', 'N/A')} V</p>
            <p><strong>MPPTs:</strong> {specs.get('mppt_count', 'N/A')}</p>
            <p><strong>Preço:</strong> R$ {p['price_brl']:,.2f if p['price_brl'] else 'Consulte'}</p>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    with open('catalogo_inversores.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Catálogo HTML gerado: catalogo_inversores.html")

# Executar
gerar_catalogo_html()
```

### Exemplo 3: Exportar para CSV

```python
import csv
import json

with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

with open('inversores_fortlev.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Nome', 'Fabricante', 'Potência (kW)', 'Voltagem (V)', 
        'MPPTs', 'Tipo', 'Fases', 'Preço (R$)', 'Arquivo Imagem'
    ])
    
    # Dados
    for p in products:
        specs = p['technical_specs']
        writer.writerow([
            p['product_id'],
            p['name'],
            p['manufacturer'],
            specs.get('power_kw', ''),
            specs.get('voltage_v', ''),
            specs.get('mppt_count', ''),
            specs.get('type', ''),
            specs.get('phases', ''),
            p['price_brl'] or '',
            p['renamed_filename']
        ])

print("CSV gerado: inversores_fortlev.csv")
```

## 🔍 Consultas Úteis

### Contar por fabricante

```python
from collections import Counter

with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

fabricantes = Counter([p['manufacturer'] for p in products])
print("\nProdutos por fabricante:")
for fab, count in fabricantes.most_common():
    print(f"  {fab}: {count}")
```

### Calcular preço médio por potência

```python
from statistics import mean

with open('inverters_image_mapping_complete.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Agrupar por faixa de potência
faixas = {
    '< 10kW': [],
    '10-30kW': [],
    '30-75kW': [],
    '> 75kW': []
}

for p in products:
    if p['price_brl'] and 'power_kw' in p['technical_specs']:
        kw = p['technical_specs']['power_kw']
        price = p['price_brl']
        
        if kw < 10:
            faixas['< 10kW'].append(price)
        elif kw < 30:
            faixas['10-30kW'].append(price)
        elif kw < 75:
            faixas['30-75kW'].append(price)
        else:
            faixas['> 75kW'].append(price)

print("\nPreço médio por faixa de potência:")
for faixa, prices in faixas.items():
    if prices:
        print(f"  {faixa}: R$ {mean(prices):,.2f}")
```

## 📦 Integração com Medusa.js

### Converter para formato Medusa

```javascript
const fs = require('fs');

// Carregar mapeamento
const mapping = JSON.parse(
  fs.readFileSync('inverters_image_mapping_complete.json', 'utf-8')
);

// Converter para formato Medusa Product
const medusaProducts = mapping.map(p => ({
  title: p.name,
  handle: p.name.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, ''),
  description: `Inversor ${p.manufacturer} - ${p.technical_specs.power_kw}kW`,
  status: 'published',
  external_id: p.product_id,
  thumbnail: `/images/${p.renamed_filename}`,
  metadata: {
    manufacturer: p.manufacturer,
    distributor: 'Fortlev',
    technical_specs: p.technical_specs,
    source: p.source
  },
  variants: [{
    title: `${p.name} - Principal`,
    sku: p.product_id,
    prices: [{
      currency_code: 'BRL',
      amount: p.price_brl ? Math.round(p.price_brl * 100) : 0
    }]
  }],
  images: [{
    url: `/images/${p.renamed_filename}`
  }]
}));

// Salvar
fs.writeFileSync(
  'medusa_products.json',
  JSON.stringify(medusaProducts, null, 2)
);

console.log(`${medusaProducts.length} produtos convertidos para Medusa`);
```

## 🎓 Dicas

1. **Sempre use `inverters_renamed_v2`** - É a versão mais recente e completa
2. **Verifique `price_brl`** - Alguns produtos não têm preço definido
3. **Use `technical_specs`** - Contém dados estruturados para filtros
4. **Códigos de imagem** - Use `image_codes` para buscar produtos

## 📞 Referências

- **Schema Medusa:** `schemas/inverters/inverters-medusa-schema.json`
- **Dados originais:** `fortlev-inverters.json`
- **Relatório completo:** `INVERTERS_RENAME_REPORT.md`
- **Resumo executivo:** `SUMMARY_INVERTERS_RENAMING.md`

---

**Última atualização:** 17/10/2025
