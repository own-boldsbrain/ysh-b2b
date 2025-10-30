# 📦 Inventário de Kits Solares - Catálogo Completo

**Última Atualização:** 19 de Outubro de 2025  
**Versão:** 1.0.0  
**Total de Kits:** 15.882  
**Distribuidores:** 4 (FortLev, FOTUS, NeoSolar, ODEX)

---

## 🎯 Navegação Rápida

- **[← Voltar para KITS_README.md](./KITS_README.md)**
- **[Ver Preços → KITS_PRICING.md](./KITS_PRICING.md)**
- **[Configuração Busca → KITS_SEARCH_CONFIG.md](./KITS_SEARCH_CONFIG.md)**

---

## 📊 Índice de Categorias

### Por Tipo de Sistema
- [Kits On-Grid (Grid-Tie)](#kits-on-grid)
  - [Micro: 0,16 - 3,0 kWp](#on-grid-micro-016-30-kwp)
  - [Pequeno: 3,0 - 10,0 kWp](#on-grid-pequeno-30-100-kwp)
  - [Médio: 10,0 - 30,0 kWp](#on-grid-medio-100-300-kwp)
  - [Grande: 30,0 - 50,0 kWp](#on-grid-grande-300-500-kwp)

- [Kits Off-Grid (Autônomo)](#kits-off-grid)
  - [Micro: 0,16 - 1,0 kWp](#off-grid-micro-016-10-kwp)
  - [Pequeno: 1,0 - 5,0 kWp](#off-grid-pequeno-10-50-kwp)
  - [Médio: 5,0 - 15,0 kWp](#off-grid-medio-50-150-kwp)

- [Kits Híbridos (Hybrid)](#kits-hibridos)
  - [Pequeno: 3,0 - 8,0 kWp](#hibrido-pequeno-30-80-kwp)
  - [Médio: 8,0 - 20,0 kWp](#hibrido-medio-80-200-kwp)
  - [Grande: 20,0 - 50,0 kWp](#hibrido-grande-200-500-kwp)

### Por Distribuidor
- [FOTUS - Kits Modulares](#distribuidor-fotus)
- [FortLev - Melhor Custo-Benefício](#distribuidor-fortlev)
- [NeoSolar - Off-Grid Specialist](#distribuidor-neosolar)
- [ODEX - Projetos Customizados](#distribuidor-odex)

---

## 🔌 Kits On-Grid

### On-Grid Micro (0,16 - 3,0 kWp)

#### FOTUS - Sistema Modular com Microinversores

##### Kit KP04-001: 1,14 kWp | Solar N Plus 570W + DEYE 2.25kW
**SKU:** `FOTUS-KP04-570-DEYE-1.14-CER-ES`

```yaml
especificacoes:
  potencia_nominal: 1.14 kWp
  tipo_sistema: On-Grid Modular
  tensao_saida: 220V Monofásico
  distribuidor: FOTUS
  disponibilidade: "✅ CD Espírito Santo"

componentes:
  paineis:
    modelo: "Solar N Plus 570W N-TYPE BIFACIAL DG"
    quantidade: 2
    potencia_unitaria: 570W
    eficiencia: 22.1%
    tecnologia: "N-Type Bifacial"
    dimensoes: "2279 x 1134 x 30 mm"
    peso: 27.5kg
    garantia_produto: 15 anos
    garantia_performance: 25 anos (84.95%)

  inversor:
    modelo: "DEYE SUN-M225G4-EU-Q0-I Microinversor"
    tipo: "Microinversor Monofásico"
    quantidade: 1
    potencia_nominal: 2250W
    mlpe_suportados: 4 painéis
    eficiencia_max: 96.7%
    tensao_entrada: "16-60V por MPPT"
    mppt_quantidade: 4 independentes
    garantia: 10 anos

  estrutura:
    tipo: "Telhado Cerâmico"
    fabricante: "CCM"
    componentes:
      - "2x Trilhos Alumínio 2.40m"
      - "1x Kit Cerâmico 4 módulos (4.8m)"
      - "1x Kit Fixação Microinversor"
    garantia: 10 anos

  eletricos:
    cabos:
      - "1x Cabo Solar 4mm² Vermelho (25m)"
      - "1x Cabo Solar 4mm² Preto (25m)"
    conectores:
      - "4x Conectores MC4 Macho/Fêmea"
    protecoes:
      - "String Box integrada"
      - "Proteção anti-ilhamento"

especificacoes_eletricas:
  entrada_dc:
    tensao_voc_total: "91.6V (2x 45.8V)"
    tensao_vmpp: "76.8V (2x 38.4V)"
    corrente_isc: "14.9A"
    corrente_impp: "14.84A"
  
  saida_ac:
    tensao_nominal: "220V / 60Hz"
    potencia_nominal: "2250W"
    corrente_maxima: "10.2A"
    fator_potencia: "> 0.99"

dados_geracao:
  geracao_media_mensal: "155-180 kWh"
  geracao_anual: "1.860-2.160 kWh"
  hsp_medio: "4.5-5.5 h/dia"
  area_necessaria: "5.2 m²"
  peso_total_sistema: "65 kg"

variacoes_estrutura:
  - codigo: "FOTUS-KP04-570-DEYE-1.14-MINI-ES"
    tipo: "Mini Trilho Alto 10cm"
    preco_adicional: "R$ 36,84"
  
  - codigo: "FOTUS-KP04-570-DEYE-1.14-FIB-ES"
    tipo: "Fibrocimento"
    preco_adicional: "R$ 52,81"

aplicacao_tipica:
  consumo_mensal: "150-200 kWh"
  perfil: "Residencial pequeno"
  instalacao: "1 dia"
  roi_estimado: "35-40% a.a."
  payback: "3-4 anos"

preco:
  kit_base: "R$ 2.507,98"
  instalacao_estimada: "R$ 376,20 (15%)"
  total_instalado: "R$ 2.884,18"
  custo_por_watt: "R$ 2,53/Wp"
```

##### Kit KP04-002: 1,20 kWp | Astronergy 600W + DEYE 2.25kW
**SKU:** `FOTUS-KP04-600-DEYE-1.20-CER-ES`

```yaml
especificacoes:
  potencia_nominal: 1.20 kWp
  tipo_sistema: On-Grid Modular
  tensao_saida: 220V Monofásico
  distribuidor: FOTUS
  disponibilidade: "✅ CD Espírito Santo"

componentes:
  paineis:
    modelo: "ASTRONERGY 600W N-TYPE BIFACIAL TIER 1"
    quantidade: 2
    potencia_unitaria: 600W
    eficiencia: 22.2%
    tecnologia: "N-Type Bifacial"
    dimensoes: "2278 x 1134 x 30 mm"
    peso: 28.2kg
    tier: "TIER 1"
    garantia_produto: 15 anos
    garantia_performance: 25 anos (85.35%)

  inversor:
    modelo: "DEYE SUN-M225G4-EU-Q0-I Microinversor"
    tipo: "Microinversor Monofásico"
    quantidade: 1
    potencia_nominal: 2250W
    mlpe_suportados: 4 painéis
    eficiencia_max: 96.7%
    tensao_entrada: "16-60V por MPPT"
    mppt_quantidade: 4 independentes
    garantia: 10 anos

  estrutura:
    tipo: "Telhado Cerâmico"
    fabricante: "CCM"
    componentes:
      - "2x Trilhos Alumínio 2.40m"
      - "1x Kit Cerâmico 4 módulos"
      - "1x Kit Fixação Microinversor"

  eletricos:
    cabos:
      - "1x Cabo Solar 4mm² Vermelho (25m)"
      - "1x Cabo Solar 4mm² Preto (25m)"
    conectores:
      - "4x Conectores MC4"

especificacoes_eletricas:
  entrada_dc:
    tensao_voc_total: "96.0V (2x 48.0V)"
    tensao_vmpp: "80.6V (2x 40.3V)"
    corrente_isc: "14.95A"
    corrente_impp: "14.89A"
  
  saida_ac:
    tensao_nominal: "220V / 60Hz"
    potencia_nominal: "2250W"
    fator_potencia: "> 0.99"

dados_geracao:
  geracao_media_mensal: "163-190 kWh"
  geracao_anual: "1.956-2.280 kWh"
  area_necessaria: "5.2 m²"
  peso_total_sistema: "67 kg"

variacoes_estrutura:
  - codigo: "FOTUS-KP04-600-DEYE-1.20-MINI-ES"
    tipo: "Mini Trilho Alto 10cm"
    preco_adicional: "R$ 41,58"
  
  - codigo: "FOTUS-KP04-600-DEYE-1.20-FIB-ES"
    tipo: "Fibrocimento"
    preco_adicional: "R$ 55,56"

aplicacao_tipica:
  consumo_mensal: "150-220 kWh"
  perfil: "Residencial pequeno"
  instalacao: "1 dia"
  roi_estimado: "38-42% a.a."
  payback: "3-4 anos"

preco:
  kit_base: "R$ 2.551,81"
  instalacao_estimada: "R$ 382,77 (15%)"
  total_instalado: "R$ 2.934,58"
  custo_por_watt: "R$ 2,44/Wp"
```

##### Kit KP04-003: 1,42 kWp | Trina 710W + DEYE 2.25kW
**SKU:** `FOTUS-KP03-710-DEYE-1.42-MINI-SE`

```yaml
especificacoes:
  potencia_nominal: 1.42 kWp
  tipo_sistema: On-Grid Modular
  tensao_saida: 220V Monofásico
  distribuidor: FOTUS
  disponibilidade: "✅ CD Sudeste - Pronta Entrega"
  destaque: "ALTA PERFORMANCE"

componentes:
  paineis:
    modelo: "TRINA 710W N-TYPE BIFACIAL TIER 1"
    quantidade: 2
    potencia_unitaria: 710W
    eficiencia: 22.90%
    tecnologia: "N-Type Bifacial TOPCon"
    dimensoes: "2384 x 1303 x 30 mm"
    peso: 34.5kg
    tier: "TIER 1"
    bifacialidade: "85%"
    garantia_produto: 15 anos
    garantia_performance: 25 anos (88.45%)

  inversor:
    modelo: "DEYE SUN-M225G4-EU-Q0-I Microinversor"
    tipo: "Microinversor Monofásico"
    quantidade: 1
    potencia_nominal: 2250W
    mlpe_suportados: 4 painéis
    eficiencia_max: 96.7%

  estrutura:
    tipo: "Mini Trilho Alto 10cm"
    fabricante: "CCM"
    observacao: "Melhor ventilação, maior eficiência"

especificacoes_eletricas:
  entrada_dc:
    tensao_voc_total: "102.2V (2x 51.1V)"
    tensao_vmpp: "86.0V (2x 43.0V)"
    corrente_isc: "14.04A"
    corrente_impp: "16.51A"
  
  saida_ac:
    tensao_nominal: "220V / 60Hz"
    potencia_nominal: "2250W"

dados_geracao:
  geracao_media_mensal: "193-224 kWh"
  geracao_anual: "2.316-2.688 kWh"
  area_necessaria: "6.2 m²"
  peso_total_sistema: "82 kg"

variacoes_estrutura:
  - codigo: "FOTUS-KP03-710-DEYE-1.42-CER-SE"
    tipo: "Cerâmico"
    preco_adicional: "R$ 48,01"
  
  - codigo: "FOTUS-KP03-710-DEYE-1.42-FIB-SE"
    tipo: "Fibrocimento"
    preco_adicional: "R$ 65,48"

aplicacao_tipica:
  consumo_mensal: "180-250 kWh"
  perfil: "Residencial médio"
  instalacao: "1 dia"
  roi_estimado: "40-45% a.a."
  payback: "3 anos"

preco:
  kit_base: "R$ 2.896,41"
  instalacao_estimada: "R$ 434,46 (15%)"
  total_instalado: "R$ 3.330,87"
  custo_por_watt: "R$ 2,34/Wp"
```

---

#### FortLev - Melhor Custo-Benefício On-Grid

##### Kit FTL-001: 2,44 kWp | Painéis 610W + Growatt 2.0kW
**SKU:** `FORTLEV-KIT-001-2.44-GROWATT-2.0-SE`

```yaml
especificacoes:
  potencia_nominal: 2.44 kWp
  tipo_sistema: On-Grid String
  tensao_saida: 220V Monofásico
  distribuidor: FortLev
  disponibilidade: "✅ Pronta Entrega Sul/Sudeste"
  destaque: "⭐ MELHOR CUSTO/BENEFÍCIO"

componentes:
  paineis:
    modelo: "Painel 610W Monofacial"
    quantidade: 4
    potencia_unitaria: ~610W
    tipo: "Mono PERC"
    eficiencia: "~21.5%"
    garantia_produto: 12 anos
    garantia_performance: 25 anos

  inversor:
    modelo: "Growatt 2.0kW Monofásico"
    tipo: "String Inverter"
    potencia_nominal: 2000W
    tensao_entrada: "50-550Vdc"
    corrente_entrada_max: "13A + 13A"
    mppt_quantidade: 2
    eficiencia_max: 98.4%
    garantia: 10 anos

  estrutura:
    tipo: "Completa p/ telhado cerâmico"
    inclusos:
      - "Trilhos alumínio"
      - "Ganchos cerâmicos"
      - "Grampos fixação"

  eletricos:
    cabos: "Cabo solar 4mm² completo"
    conectores: "MC4 padrão"
    protecoes: "String Box incluída"

especificacoes_eletricas:
  entrada_dc:
    potencia_max: 2600W
    tensao_inicial: "125Vdc (arranjo exemplo)"
    tensao_mppt: "80-520Vdc"
  
  saida_ac:
    potencia_nominal: 2000W
    tensao: "220V / 60Hz"
    corrente_max: "9.5A"

dados_geracao:
  geracao_media_mensal: "331-385 kWh"
  geracao_anual: "3.972-4.620 kWh"
  area_necessaria: "~10 m²"

aplicacao_tipica:
  consumo_mensal: "280-380 kWh"
  perfil: "Residencial médio"
  instalacao: "1-2 dias"
  roi_estimado: "35% a.a."
  payback: "~4 anos"

preco:
  kit_base: "R$ 2.923,56"
  instalacao_estimada: "R$ 438,53 (15%)"
  total_instalado: "R$ 3.362,09"
  custo_por_watt: "R$ 1,38/Wp"
  economia_vs_mercado: "~40% mais barato"
```

##### Kit FTL-002: 2,52 kWp | LONGi 630W + Growatt 2.0kW
**SKU:** `FORTLEV-KIT-002-2.52-LONGI-GROWATT-SE`

```yaml
especificacoes:
  potencia_nominal: 2.52 kWp
  tipo_sistema: On-Grid String
  tensao_saida: 220V Monofásico
  distribuidor: FortLev
  disponibilidade: "✅ Pronta Entrega"
  destaque: "⭐ RECOMENDADO - Melhor Relação Custo x Geração"

componentes:
  paineis:
    modelo: "LONGi 630W Hi-MO 6"
    quantidade: 4
    potencia_unitaria: 630W
    eficiencia: 22.3%
    tecnologia: "Mono PERC"
    tier: "TIER 1"
    garantia_produto: 15 anos
    garantia_performance: 25 anos (84.8%)

  inversor:
    modelo: "Growatt MIC 2000TL-X"
    tipo: "String Inverter"
    potencia_nominal: 2000W
    eficiencia_max: 98.4%
    mppt: 2 independentes
    garantia: 10 anos

dados_geracao:
  geracao_media_mensal: "342-398 kWh"
  geracao_anual: "4.104-4.776 kWh"

aplicacao_tipica:
  consumo_mensal: "290-400 kWh"
  perfil: "Residencial médio"
  roi_estimado: "40% a.a."
  payback: "3-4 anos"

preco:
  kit_base: "R$ 3.163,70"
  instalacao_estimada: "R$ 474,56 (15%)"
  total_instalado: "R$ 3.638,26"
  custo_por_watt: "R$ 1,44/Wp"
```

---

### On-Grid Pequeno (3,0 - 10,0 kWp)

##### Kit FOTUS KP04-004: 2,28 kWp | Solar N Plus 570W (4x) + DEYE 2.25kW
**SKU:** `FOTUS-KP04-570X4-DEYE-2.28-CER-ES`

```yaml
especificacoes:
  potencia_nominal: 2.28 kWp
  tipo_sistema: On-Grid Modular
  tensao_saida: 220V Monofásico
  distribuidor: FOTUS
  disponibilidade: "✅ CD Espírito Santo"

componentes:
  paineis:
    modelo: "Solar N Plus 570W N-TYPE BIFACIAL DG"
    quantidade: 4
    potencia_total: 2280W
    eficiencia: 22.1%
    tecnologia: "N-Type Bifacial"
    frame: "Fibra de Vidro (leve)"

  inversor:
    modelo: "DEYE SUN-M225G4-EU-Q0-I"
    tipo: "Microinversor"
    potencia_nominal: 2250W
    mlpe_max: 4 painéis
    mppt: 4 independentes

  estrutura:
    tipo: "Telhado Cerâmico CCM"
    trilhos: "4x 2.40m"
    kit_fixacao: "4 módulos (4.8m)"

especificacoes_eletricas:
  entrada_dc:
    tensao_voc_total: "183.2V (4x 45.8V)"
    potencia_max: 2280W
  
  saida_ac:
    potencia_nominal: 2250W
    tensao: "220V / 60Hz"

dados_geracao:
  geracao_media_mensal: "310-360 kWh"
  geracao_anual: "3.720-4.320 kWh"
  area_necessaria: "10.4 m²"
  peso_total: "130 kg"

variacoes:
  - codigo: "FOTUS-KP04-570X4-DEYE-2.28-MINI-ES"
    estrutura: "Mini Trilho Alto"
    preco: "R$ 3.465,11"
  
  - codigo: "FOTUS-KP04-570X4-DEYE-2.28-FIB-ES"
    estrutura: "Fibrocimento"
    preco: "R$ 3.497,51"

aplicacao:
  consumo_mensal: "300-450 kWh"
  perfil: "Residencial médio/comercial pequeno"
  instalacao: "1-2 dias"
  roi: "38-42% a.a."
  payback: "3-4 anos"

preco:
  kit_ceramico: "R$ 3.481,31"
  instalacao: "R$ 522,20 (15%)"
  total: "R$ 4.003,51"
  custo_watt: "R$ 1,75/Wp"
```

##### Kit FOTUS KP04-005: 2,40 kWp | Astronergy 600W (4x) + DEYE 2.25kW
**SKU:** `FOTUS-KP04-600X4-DEYE-2.40-MINI-ES`

```yaml
especificacoes:
  potencia_nominal: 2.40 kWp
  tipo_sistema: On-Grid Modular
  distribuidor: FOTUS
  disponibilidade: "✅ CD Espírito Santo"

componentes:
  paineis:
    modelo: "ASTRONERGY 600W N-TYPE BIFACIAL TIER 1"
    quantidade: 4
    potencia_total: 2400W
    eficiencia: 22.2%
    tier: "TIER 1"

  inversor:
    modelo: "DEYE SUN-M225G4-EU-Q0-I"
    potencia_nominal: 2250W
    mlpe_max: 4

  estrutura:
    tipo: "Mini Trilho Alto 10cm CCM"
    vantagem: "Melhor ventilação = +2-3% geração"

dados_geracao:
  geracao_media_mensal: "326-379 kWh"
  geracao_anual: "3.912-4.548 kWh"
  area_necessaria: "10.4 m²"

aplicacao:
  consumo_mensal: "310-470 kWh"
  perfil: "Residencial médio"
  roi: "40% a.a."
  payback: "3 anos"

preco:
  kit_mini_trilho: "R$ 3.541,81"
  instalacao: "R$ 531,27 (15%)"
  total: "R$ 4.073,08"
  custo_watt: "R$ 1,70/Wp"

variacoes:
  ceramico: "R$ 3.642,59"
  fibrocimento: "R$ 3.655,77"
```

##### Kit FortLev Médio: 5,0 kWp | Painéis 625W (8x) + Growatt 5.0kW
**SKU:** `FORTLEV-KIT-MED-5.0-GROWATT-SE`

```yaml
especificacoes:
  potencia_nominal: 5.0 kWp
  tipo_sistema: On-Grid String
  tensao_saida: 220V Monofásico
  distribuidor: FortLev
  disponibilidade: "✅ Pronta Entrega"
  aplicacao: "Residencial Grande / Comercial Pequeno"

componentes:
  paineis:
    modelo: "Painel 625W Mono PERC"
    quantidade: 8
    potencia_total: 5000W
    eficiencia: "~21.8%"

  inversor:
    modelo: "Growatt 5000TL3-S"
    tipo: "String Inverter Monofásico"
    potencia_nominal: 5000W
    tensao_mppt: "80-550Vdc"
    mppt: 2 independentes
    eficiencia_max: 98.4%

  estrutura:
    tipo: "Telhado Cerâmico Completo"
    inclusos:
      - "Trilhos alumínio"
      - "Ganchos e grampos"
      - "Sistema aterramento"

especificacoes_eletricas:
  entrada_dc:
    potencia_max: 6500W (oversizing 130%)
    configuracao_sugerida: "2 strings x 4 painéis"
    tensao_string: "~170Vdc"
  
  saida_ac:
    potencia_nominal: 5000W
    corrente_max: 25A

dados_geracao:
  geracao_media_mensal: "679-789 kWh"
  geracao_anual: "8.148-9.468 kWh"
  area_necessaria: "~27 m²"

aplicacao:
  consumo_mensal: "600-950 kWh"
  perfil: "Residencial grande / Comercial"
  instalacao: "2-3 dias"
  roi: "38% a.a."
  payback: "3-4 anos"

preco:
  kit_base: "R$ 14.500,00" # estimado
  instalacao: "R$ 2.900,00 (20%)"
  total: "R$ 17.400,00"
  custo_watt: "R$ 3,48/Wp"
```

---

### On-Grid Médio (10,0 - 30,0 kWp)

##### Kit Comercial: 15,0 kWp | Painéis 600W (25x) + Growatt 15kW Trifásico
**SKU:** `COMMERCIAL-15KW-GROWATT-TRI`

```yaml
especificacoes:
  potencia_nominal: 15.0 kWp
  tipo_sistema: On-Grid String Trifásico
  tensao_saida: 220/380V Trifásico
  aplicacao: "Comercial Médio"
  target: "Empresas, indústrias pequenas"

componentes:
  paineis:
    modelo: "Painel 600W Half-Cell Bifacial"
    quantidade: 25
    potencia_total: 15000W
    eficiencia: 21.5%
    configuracao: "5 strings x 5 painéis"

  inversor:
    modelo: "Growatt 15000TL3-S"
    tipo: "String Inverter Trifásico"
    potencia_nominal: 15000W
    tensao_mppt: "200-850Vdc"
    mppt: 2 independentes
    eficiencia_max: 98.6%
    comunicacao: "WiFi, RS485"
    garantia: 10 anos

  estrutura:
    tipo: "Laje ou Solo"
    material: "Alumínio + Aço galvanizado"
    inclinacao: "15° ajustável"

especificacoes_eletricas:
  entrada_dc:
    potencia_max: 19500W (oversizing 130%)
    tensao_operacao: "~230Vdc por string"
  
  saida_ac:
    potencia_nominal: 15000W
    corrente_por_fase: 23A

dados_geracao:
  geracao_media_mensal: "2.037-2.368 kWh"
  geracao_anual: "24.444-28.416 kWh"
  area_necessaria: "82 m²"
  peso_total: "~900 kg"

aplicacao:
  consumo_mensal: "1.800-2.800 kWh"
  perfil: "Comércio médio, pequena indústria"
  instalacao: "5-7 dias"
  roi: "42% a.a."
  payback: "4-5 anos"

preco:
  kit_base: "R$ 42.000,00" # estimado
  instalacao: "R$ 8.400,00 (20%)"
  total: "R$ 50.400,00"
  custo_watt: "R$ 3,36/Wp"
```

---

## 🔋 Kits Off-Grid

### Off-Grid Micro (0,16 - 1,0 kWp)

#### NeoSolar - Especialista em Sistemas Isolados

##### Kit OFF-001: 0,16 kWp | Sistema Básico Iluminação
**SKU:** `NEOSOLAR-OFF-BASIC-160W`

```yaml
especificacoes:
  potencia_nominal: 0.16 kWp (160W)
  tipo_sistema: Off-Grid Autônomo
  tensao_sistema: 12Vdc
  distribuidor: NeoSolar
  aplicacao: "Iluminação remota, pequenos dispositivos"

componentes:
  paineis:
    modelo: "Resun 160W Policristalino"
    quantidade: 1
    potencia: 160W
    voc: 21.6V
    isc: 9.8A
    garantia: 10 anos

  controlador:
    modelo: "Controlador PWM 10A 12V"
    tipo: "PWM"
    corrente_max: 10A
    tensao_sistema: 12V
    protecoes: "Sobrecarga, curto, inversão"

  bateria:
    tipo: "Selada VRLA 12V"
    capacidade: "100Ah (1.2kWh)"
    tensao: 12V
    vida_util: "5-7 anos"
    ciclos: "~1500 (50% DoD)"

  inversor:
    modelo: "Inversor 12V/220V 300W"
    potencia_continua: 300W
    potencia_pico: 600W
    forma_onda: "Senoidal pura"

dados_energia:
  geracao_diaria: "0.72-0.88 kWh"
  capacidade_armazenamento: "1.2 kWh"
  autonomia: "1-2 dias sem sol"
  carga_utilizavel: "0.6 kWh (50% DoD)"

aplicacao:
  uso_tipico:
    - "Iluminação LED (40W x 5h)"
    - "Carregamento celular"
    - "Rádio/pequenos eletrônicos"
  perfil: "Propriedade rural isolada"
  instalacao: "4-6 horas"

preco:
  kit_completo: "R$ 2.800,00" # estimado
  instalacao: "R$ 420,00 (15%)"
  total: "R$ 3.220,00"
  custo_watt: "R$ 20,13/Wp"
```

##### Kit OFF-002: 0,50 kWp | Sistema Bombeamento Água
**SKU:** `NEOSOLAR-OFF-PUMP-500W`

```yaml
especificacoes:
  potencia_nominal: 0.50 kWp (500W)
  tipo_sistema: Off-Grid Bombeamento
  tensao_sistema: 24Vdc
  aplicacao: "Bombeamento água poços rasos"

componentes:
  paineis:
    modelo: "Canadian Solar 250W"
    quantidade: 2
    potencia_total: 500W
    configuracao: "2 painéis série (24V)"

  controlador:
    modelo: "MPPT 20A 24V"
    tipo: "MPPT"
    eficiencia: 98%

  bateria:
    tipo: "Chumbo-ácido estacionária"
    capacidade: "2x 150Ah (3.6kWh @ 24V)"
    configuracao: "Série 24V"

  bomba:
    modelo: "Bomba Solar DC 24V"
    vazao: "2000 L/h"
    altura_max: "20m"
    potencia: 400W

dados_operacao:
  geracao_diaria: "2.25-2.75 kWh"
  bombeamento_diario: "8.000-12.000 litros"
  horas_operacao: "5-7h (dependente sol)"

aplicacao:
  uso: "Irrigação, abastecimento rural"
  profundidade_max: "20m"
  distancia_max: "100m horizontal"

preco:
  kit_completo: "R$ 6.500,00" # estimado
  instalacao: "R$ 1.300,00 (20%)"
  total: "R$ 7.800,00"
```

---

### Off-Grid Pequeno (1,0 - 5,0 kWp)

##### Kit OFF-003: 3,0 kWp | Sistema Residencial Completo
**SKU:** `NEOSOLAR-OFF-RES-3KW-LITHIUM`

```yaml
especificacoes:
  potencia_nominal: 3.0 kWp
  tipo_sistema: Off-Grid Residencial
  tensao_sistema: 48Vdc
  aplicacao: "Residência isolada completa"
  destaque: "Sistema com baterias lítio LFP"

componentes:
  paineis:
    modelo: "Trina 550W Half-Cell"
    quantidade: 6
    potencia_total: 3300W
    configuracao: "2 strings x 3 painéis"

  inversor_carregador:
    modelo: "Growatt SPF 3000TL HVM"
    tipo: "Inversor/Carregador Off-Grid"
    potencia_continua: 3000W
    potencia_pico: 6000W
    tensao_bateria: 48V
    corrente_carga_max: 80A
    mppt: "Integrado"
    forma_onda: "Senoidal pura"
    bypass: "Automático (rede/gerador)"

  baterias:
    tipo: "Lítio LFP (LiFePO4)"
    modelo: "DYNESS PowerBox Pro 5.12kWh"
    quantidade: 2
    capacidade_total: 10.24kWh
    tensao_nominal: 48V
    bms: "Integrado"
    ciclos_vida: 6000 (80% DoD)
    garantia: 10 anos
    comunicacao: "CAN/RS485"

  controlador_carga:
    tipo: "MPPT Integrado no inversor"
    tensao_entrada_max: 450Vdc
    corrente_max: 80A
    eficiencia: 98%

  estrutura:
    tipo: "Telhado Metálico"
    fabricante: "SOLAR GROUP"
    componentes:
      - "Grampos metálicos específicos"
      - "Trilhos alumínio"
      - "Sistema aterramento"

especificacoes_eletricas:
  entrada_pv:
    potencia_max: 4000W
    tensao_mppt: "120-450Vdc"
    tensao_voc_max: 450Vdc
  
  sistema_bateria:
    tensao_nominal: 48V
    capacidade_util: 8.2kWh (80% DoD)
    corrente_carga_max: 80A
    corrente_descarga_max: 100A
  
  saida_ac:
    potencia_continua: 3000W
    potencia_pico: 6000W
    tensao: "220V / 60Hz"
    forma_onda: "Senoidal pura (THD < 3%)"

dados_energia:
  geracao_media_diaria: "15-18 kWh"
  capacidade_armazenamento: 10.24kWh
  energia_utilizavel: 8.2kWh
  autonomia_sem_sol: "2-3 dias (carga completa)"
  tempo_recarga: "6-8 horas (sol pleno)"

cargas_suportadas:
  simultaneas:
    - "Geladeira duplex (200W)"
    - "Iluminação LED (300W)"
    - "TV + Eletrônicos (150W)"
    - "Bomba água (500W)"
    - "Ventiladores (200W)"
  total_simultaneo: "~1.350W"
  
  pico_curto:
    - "Máquina lavar (até 2000W - 30min)"
    - "Micro-ondas (1200W - 10min)"
    - "Ferro elétrico (1500W - 15min)"

aplicacao:
  consumo_diario: "6-8 kWh"
  pessoas: "3-5"
  perfil: "Residência rural isolada"
  backup_gerador: "Opcional (entrada auxiliar)"
  instalacao: "3-5 dias"

geracao_backup:
  entrada_auxiliar: "Sim (220V AC)"
  uso: "Recarga baterias dias nublados"
  potencia_max_gerador: "5kVA"
  tipo_recomendado: "Gerador diesel/gasolina"

preco:
  paineis: "R$ 9.900,00"
  inversor: "R$ 8.500,00"
  baterias_litio: "R$ 28.000,00"
  estrutura: "R$ 2.400,00"
  eletricos: "R$ 1.800,00"
  kit_total: "R$ 50.600,00"
  instalacao: "R$ 10.120,00 (20%)"
  total_instalado: "R$ 60.720,00"
  custo_watt: "R$ 20,24/Wp"

comparacao_chumbo_acido:
  baterias_alternative: "8x 220Ah estacionária"
  custo_baterias: "R$ 14.000,00"
  vida_util: "4-6 anos"
  substituicao_25anos: "4-5 vezes"
  custo_total_25anos: "R$ 70.000,00"
  observacao: "Lítio mais caro inicial, economiza longo prazo"
```

---

## ⚡ Kits Híbridos

### Híbrido Pequeno (3,0 - 8,0 kWp)

##### Kit HYB-001: 5,0 kWp | Residencial com Backup
**SKU:** `HYBRID-RES-5KW-DYNESS-HV`

```yaml
especificacoes:
  potencia_nominal: 5.0 kWp
  tipo_sistema: Híbrido (On-Grid + Backup)
  tensao_saida: 220V Monofásico
  aplicacao: "Residencial com backup crítico"
  destaque: "Backup automático < 10ms"

componentes:
  paineis:
    modelo: "LONGi 625W Hi-MO 6 TIER 1"
    quantidade: 8
    potencia_total: 5000W
    eficiencia: 22.3%
    configuracao: "2 strings x 4 painéis"

  inversor_hibrido:
    modelo: "Growatt SPH 5000"
    tipo: "Inversor Híbrido Monofásico"
    potencia_ac_nominal: 5000W
    potencia_pv_max: 6500W
    tensao_bateria: "180-550Vdc (alta tensão)"
    corrente_carga_bateria: 25A
    mppt: 2 independentes
    backup_time: "< 10ms (UPS mode)"
    garantia: 10 anos

  baterias_alta_tensao:
    tipo: "Lítio LFP Alta Tensão"
    modelo: "DYNESS PowerBox Pro HV 5.12kWh"
    quantidade: 2
    capacidade_total: 10.24kWh
    tensao_nominal: 400Vdc (empilhável)
    bms: "Integrado + Comunicação CAN"
    ciclos_vida: 6000 (80% DoD)
    garantia: 10 anos
    expansao_max: "até 20.48kWh (4 unidades)"

  estrutura:
    tipo: "Telhado Cerâmico"
    trilhos: "6x 2.40m"

especificacoes_eletricas:
  entrada_pv:
    potencia_max_pv: 6500W
    tensao_mppt: "120-550Vdc"
    corrente_max_mppt: "13A + 13A"
  
  sistema_bateria:
    tensao_nominal: 400Vdc
    capacidade_utilizavel: 8.2kWh (80% DoD)
    potencia_carga_max: 5000W
    potencia_descarga_max: 5000W
  
  saida_ac:
    potencia_continua: 5000W
    corrente_max: 25A
    fator_potencia: 1.0

modos_operacao:
  1_modo_solar:
    prioridade: "Solar → Casa → Bateria → Rede"
    descricao: "Maximiza uso solar"
  
  2_modo_bateria:
    prioridade: "Solar → Bateria → Casa → Rede"
    descricao: "Armazenamento prioritário"
  
  3_modo_rede:
    prioridade: "Solar → Casa → Rede (vende) + Bateria"
    descricao: "Maximiza créditos rede"
  
  4_modo_backup:
    ativacao: "Automática em queda rede"
    tempo_comutacao: "< 10ms"
    cargas: "Críticas selecionadas"
  
  5_modo_economia:
    funcao: "Otimiza tarifação"
    ponta: "Usa bateria"
    fora_ponta: "Carrega bateria + uso solar"

dados_energia:
  geracao_media_diaria: "22-27 kWh"
  capacidade_backup: 8.2kWh
  autonomia_backup: "4-6 horas (cargas críticas)"
  tempo_recarga_bateria: "3-5 horas (sol)"

cargas_backup_criticas:
  circuitos:
    - "Geladeira/Freezer"
    - "Iluminação essencial"
    - "Internet/Roteador"
    - "Bomba água"
    - "Tomadas críticas"
  potencia_total: "~1.500W"
  autonomia: "5-6 horas"

aplicacao:
  consumo_diario: "18-25 kWh"
  perfil: "Residência média/alta"
  beneficios:
    - "Economia conta luz"
    - "Backup automático"
    - "Independência gradual"
    - "Arbitragem tarifária"
  instalacao: "2-3 dias"
  roi: "42% a.a."
  payback: "3-4 anos"

preco:
  paineis: "R$ 15.000,00"
  inversor_hibrido: "R$ 12.000,00"
  baterias_hv: "R$ 22.000,00"
  estrutura: "R$ 2.500,00"
  eletricos_monitoramento: "R$ 2.000,00"
  kit_total: "R$ 53.500,00"
  instalacao: "R$ 10.700,00 (20%)"
  total_instalado: "R$ 64.200,00"
  custo_watt: "R$ 12,84/Wp"

economia_anual:
  consumo_atual: "700 kWh/mês"
  tarifa_media: "R$ 0,85/kWh"
  conta_atual: "R$ 595,00/mês"
  reducao_esperada: "85%"
  nova_conta: "R$ 89,25/mês (mínima)"
  economia_mensal: "R$ 505,75"
  economia_anual: "R$ 6.069,00"
  roi_calculado: "9,5% a.a. (sem bateria seria 35%)"
```

---

### Híbrido Médio (8,0 - 20,0 kWp)

##### Kit HYB-002: 10,0 kWp | Comercial com Backup Total
**SKU:** `HYBRID-COM-10KW-DYNESS-TOWER`

```yaml
especificacoes:
  potencia_nominal: 10.0 kWp
  tipo_sistema: Híbrido Trifásico
  tensao_saida: 220/380V Trifásico
  aplicacao: "Comercial/pequena indústria"
  destaque: "Backup total + arbitragem tarifária"

componentes:
  paineis:
    modelo: "Trina 710W N-TYPE BIFACIAL TIER 1"
    quantidade: 14
    potencia_total: 9940W (~10kWp)
    eficiencia: 22.9%
    configuracao: "2 strings x 7 painéis"

  inversor_hibrido:
    modelo: "Growatt MOD 10KTL3-XH"
    tipo: "Inversor Híbrido Trifásico"
    potencia_ac_nominal: 10000W
    potencia_pv_max: 13000W
    tensao_bateria: "180-600Vdc HV"
    mppt: 2 independentes
    backup: "< 10ms UPS"
    garantia: 10 anos

  baterias:
    modelo: "DYNESS Tower T14 (14kWh)"
    quantidade: 2
    capacidade_total: 28kWh
    tensao_nominal: 400Vdc
    modular: "Expansível até 56kWh"
    ciclos: 6000
    garantia: 10 anos

especificacoes_eletricas:
  entrada_pv: 
    potencia_max: 13000W
    oversizing: "130%"
  
  bateria:
    capacidade_util: 22.4kWh (80% DoD)
  
  saida_ac:
    potencia_trifasica: 10000W
    balanceamento_fases: "Automático"

dados_energia:
  geracao_media_diaria: "45-54 kWh"
  backup_disponivel: 22.4kWh
  autonomia_backup_total: "3-4 horas"
  autonomia_cargas_criticas: "8-12 horas"

modos_avancados:
  arbitragem_tarifaria:
    horario_ponta: "18h-21h"
    acao: "Usa 100% bateria"
    economia_mensal: "R$ 800-1.200"
  
  demanda_contratada:
    funcao: "Reduz picos demanda"
    economia_anual: "R$ 3.600-6.000"

aplicacao:
  consumo_mensal: "1.200-1.800 kWh"
  perfil: "Comércio/pequena indústria"
  roi: "38% a.a."
  payback: "4-5 anos"

preco:
  kit_total: "R$ 98.000,00"
  instalacao: "R$ 19.600,00 (20%)"
  total: "R$ 117.600,00"
  custo_watt: "R$ 11,76/Wp"
```

---

## 📍 Distribuidores Detalhados

### Distribuidor: FOTUS

**Especialidade:** Sistemas modulares com microinversores  
**Região de Atendimento:** Espírito Santo (CD principal), Sudeste  
**Disponibilidade:** ✅ Pronta entrega  
**Diferencial:** Flexibilidade e escalabilidade

#### Portfólio FOTUS

**Marcas de Painéis:**
- ASTRONERGY (TIER 1) - N-Type Bifacial 22.2%
- Solar N Plus - N-Type Bifacial 22.1% (Frame Fibra de Vidro)
- TRINA (TIER 1) - N-Type Bifacial 22.9%

**Marcas de Inversores:**
- DEYE - Microinversores 2.25kW (4 MLPE)
- TSUNESS - Microinversores 2.25kW (4 MLPE)

**Estruturas:**
- CCM - Telhado cerâmico, mini trilho, fibrocimento
- SOLAR GROUP - Fibrocimento fixação lateral

**Faixas de Potência:**
- 1,14 - 2,40 kWp (sistemas micro)
- 2,28 - 4,80 kWp (sistemas pequenos)
- Expansível modularmente

**Vantagens:**
- Redundância (falha de 1 micro não para sistema)
- Monitoramento painel a painel
- Instalação simplificada
- Expansão futura facilitada

**Desvantagens:**
- Custo/Watt superior (R$ 1,70-2,50/Wp)
- Limitado a sistemas pequenos/médios

---

### Distribuidor: FortLev

**Especialidade:** Kits on-grid custo-benefício  
**Região de Atendimento:** Sul, Sudeste (pronta entrega)  
**Disponibilidade:** ✅ Pronta entrega  
**Diferencial:** ⭐ MELHOR PREÇO DO MERCADO

#### Portfólio FortLev

**Marcas de Painéis:**
- LONGi (TIER 1) - 630W Hi-MO 6
- Canadian Solar - 625W Mono PERC
- JA Solar - 610W Half-Cell

**Marcas de Inversores:**
- Growatt - Série MIC/TL 2-15kW
- Solis - String inversores
- SAJ - Linha residencial/comercial

**Estruturas:**
- Completas para telhado cerâmico
- Adaptadores metálico/fibrocimento
- Laje (sistemas maiores)

**Faixas de Potência:**
- 2,0 - 15,0 kWp
- Foco residencial médio/grande

**Vantagens:**
- ⭐ Melhor custo-benefício (R$ 1,20-1,50/Wp)
- Kits completos prontos
- Marcas TIER 1 a preço competitivo
- Logística eficiente

**Desvantagens:**
- Menos flexibilidade composição
- Foco on-grid (não atende off-grid)

---

### Distribuidor: NeoSolar

**Especialidade:** Sistemas off-grid e isolados  
**Região de Atendimento:** Nacional  
**Disponibilidade:** ✅ Estoque nacional  
**Diferencial:** Expertise em baterias e autonomia

#### Portfólio NeoSolar

**Marcas de Painéis:**
- Resun - Linha off-grid 160-330W
- Canadian Solar - Linha premium
- BYD - Integração painéis + baterias

**Inversores/Carregadores:**
- Must - Off-grid 1-10kW
- Schneider - Linha Conext
- Victron - Premium off-grid

**Baterias:**
- BYD - Lítio LFP alta voltagem
- Moura - Estacionárias chumbo-ácido
- Freedom - Lítio nacional
- DYNESS - Modular empilhável

**Faixas de Potência:**
- 0,16 - 1,0 kWp (micro off-grid)
- 1,0 - 10,0 kWp (residencial off-grid)
- Sistemas híbridos sob consulta

**Vantagens:**
- Especialização off-grid
- Consultoria dimensionamento
- Suporte técnico especializado
- Maior variedade baterias

**Desvantagens:**
- Custo/Watt elevado (off-grid sempre mais caro)
- Prazo entrega componentes variável

---

### Distribuidor: ODEX

**Especialidade:** Componentes avulsos e projetos customizados  
**Região de Atendimento:** Conforme estoque  
**Disponibilidade:** ⚠️ Variável por produto  
**Diferencial:** Flexibilidade total

#### Portfólio ODEX

**Painéis (Múltiplas Marcas):**
- Conforme disponibilidade estoque
- 400-700W
- Tecnologias: Mono PERC, Half-Cell, Bifacial

**Inversores:**
- SAJ - R5 Series (3-10kW)
- Growatt - Linha completa
- Solis - String inversores
- Outros conforme estoque

**Estruturas:**
- Solar Group
- CCM
- Pratyc
- Customizadas sob projeto

**Componentes Elétricos:**
- Cabos solares 4/6/10mm²
- Conectores MC4 diversas marcas
- String Box completas
- DPS, disjuntores, fusíveis

**Vantagens:**
- Projeto 100% customizado
- Melhor custo em grandes volumes
- Variedade componentes
- Atende especificações técnicas exatas

**Desvantagens:**
- Requer projeto prévio
- Disponibilidade variável
- Prazo entrega componentes diferentes
- Maior complexidade logística

---

## 📊 Resumo Estatístico

### Distribuição por Tipo de Sistema

```yaml
on_grid:
  total_kits: 12.450
  faixa_potencia: "0,16 - 50,0 kWp"
  distribuidores: "FOTUS, FortLev, ODEX"
  preco_medio_kwp: "R$ 1,20 - 3,50/Wp"

off_grid:
  total_kits: 2.180
  faixa_potencia: "0,16 - 15,0 kWp"
  distribuidores: "NeoSolar, ODEX"
  preco_medio_kwp: "R$ 15,00 - 25,00/Wp"

hibrido:
  total_kits: 1.252
  faixa_potencia: "3,0 - 50,0 kWp"
  distribuidores: "NeoSolar, ODEX (customizado)"
  preco_medio_kwp: "R$ 8,00 - 15,00/Wp"
```

### Distribuidores por Volume

```yaml
fotus:
  total_skus: 8.200
  especialidade: "Modulares micro"
  ticket_medio: "R$ 3.500,00"

fortlev:
  total_skus: 4.850
  especialidade: "On-grid custo-benefício"
  ticket_medio: "R$ 5.200,00"

neosolar:
  total_skus: 2.180
  especialidade: "Off-grid/baterias"
  ticket_medio: "R$ 18.500,00"

odex:
  total_skus: 652
  especialidade: "Customizados"
  ticket_medio: "R$ 12.000,00"
```

---

## 🔗 Links e Referências

**Documentação Relacionada:**
- [KITS_README.md](./KITS_README.md) - Visão geral completa
- [KITS_PRICING.md](./KITS_PRICING.md) - Matriz de preços
- [KITS_SEARCH_CONFIG.md](./KITS_SEARCH_CONFIG.md) - Configuração busca
- [MARKETPLACE_KIT_RULES.md](../docs/MARKETPLACE_KIT_RULES.md) - Regras comerciais

**Componentes:**
- [PAINEIS_README.md](./PAINEIS_README.md) - Painéis fotovoltaicos
- [INVERSORES_README.md](./INVERSORES_README.md) - Inversores
- [BATERIAS_README.md](./BATERIAS_README.md) - Sistemas armazenamento

---

**Última Atualização:** 19 de Outubro de 2025  
**Próxima Revisão:** Quinzenal (estoque dinâmico)  
**Contato Técnico:** suporte@yellosolarhub.com

---

*Inventário gerado automaticamente - YSH B2B Platform*
