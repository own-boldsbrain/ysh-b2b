# Inversores - Padrão SKU YSH

## Visão Geral

Este documento estabelece os padrões de nomenclatura (SKU) para inversores fotovoltaicos utilizados nos projetos YSH Solar. O padrão garante identificação precisa dos diferentes tipos de inversores e suas especificações técnicas.

## Padrão SKU

### Formato

```text
INV-{MANUFACTURER}-{MODEL}-{POWER}KW[-{TYPE}]
```

### Componentes da SKU

1. **INV**: Prefixo fixo identificando inversores
2. **MANUFACTURER**: Código de 3-5 letras do fabricante
3. **MODEL**: Modelo específico do inversor
4. **POWER**: Potência nominal em kW
5. **TYPE**: Tipo opcional (GT, HYB, OG, MICRO, OPT)

### Exemplos

- `INV-GROW-MIN-5000TL-X-5KW-GT`
- `INV-DEYE-SUN-8K-SG04LP3-8KW-HYB`
- `INV-SOLIS-S6-GR1P3K-3KW-GT`

## Fabricantes Aprovados

### Tier 1 (Premium)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| GROW | Growatt | China | Residencial, Híbrido |
| DEYE | Deye | China | Híbrido, Storage |
| SOLIS | Solis | China | Residencial, Comercial |
| GOOD | GoodWe | China | Híbrido, Storage |

### Tier 2 (Performance)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| FRON | Fronius | Áustria | Residencial Premium |
| SMA | SMA | Alemanha | Comercial, Industrial |
| SUNG | Sungrow | China | Utility Scale |
| HUAW | Huawei | China | Smart Inverters |

## Tipos de Inversores

### Grid-Tie (GT)

- **Descrição**: Conectados à rede elétrica
- **Aplicação**: Sistemas sem backup
- **Potência**: 0.6kW - 1000kW
- **Características**: Alta eficiência, baixo custo

### Híbrido (HYB)

- **Descrição**: Grid-tie com backup de bateria
- **Aplicação**: Sistemas com armazenamento
- **Potência**: 3kW - 50kW
- **Características**: Gestão inteligente de energia

### Off-Grid (OG)

- **Descrição**: Sistemas isolados da rede
- **Aplicação**: Locais remotos
- **Potência**: 1kW - 20kW
- **Características**: Controle de carga, autonomia total

### Microinversores (MICRO)

- **Descrição**: Um inversor por painel
- **Aplicação**: Sistemas residenciais
- **Potência**: 0.25kW - 0.5kW
- **Características**: Otimização individual, monitoramento

### Otimizadores (OPT)

- **Descrição**: DC/DC conversores + inversor string
- **Aplicação**: Sombreamento parcial
- **Potência**: 0.3kW - 0.6kW por otimizador
- **Características**: MPPT individual, segurança

## Especificações Técnicas

### Campos Obrigatórios

- `manufacturer`: Fabricante do inversor
- `model`: Modelo específico
- `power_rating_kw`: Potência nominal em kW
- `inverter_type`: Tipo do inversor
- `efficiency_percent`: Eficiência máxima
- `input_voltage_range`: Faixa de tensão DC
- `output_voltage`: Tensão de saída AC
- `phases`: Número de fases (1 ou 3)
- `mppt_trackers`: Número de rastreadores MPPT
- `warranty_years`: Garantia em anos

### Campos Opcionais

- `max_input_current`: Corrente máxima de entrada
- `starting_voltage`: Tensão de partida
- `max_efficiency_percent`: Eficiência europeia
- `power_factor`: Fator de potência
- `thd_percent`: Distorção harmônica total
- `operating_temp_range`: Faixa de temperatura
- `ip_rating`: Grau de proteção
- `certifications`: Certificações
- `communication_protocols`: Protocolos de comunicação
- `battery_compatibility`: Compatibilidade com baterias

## Faixas de Potência

### Residencial (1-15kW)

- **Monofásico**: 1kW - 6kW
- **Trifásico**: 3kW - 15kW
- **Aplicação**: Residências, pequenos comércios
- **Características**: Compacto, silencioso

### Comercial (15-125kW)

- **Trifásico**: 15kW - 125kW
- **Aplicação**: Empresas, indústrias médias
- **Características**: Alta eficiência, monitoramento avançado

### Industrial (125kW+)

- **Trifásico**: 125kW - 1000kW+
- **Aplicação**: Grandes indústrias, usinas
- **Características**: Redundância, controle avançado

## Exemplos de Produtos

### Growatt MIN 5000TL-X

```json
{
  "sku": "INV-GROW-MIN-5000TL-X-5KW-GT",
  "manufacturer": "Growatt",
  "model": "MIN 5000TL-X",
  "power_rating_kw": 5.0,
  "inverter_type": "GRID_TIE",
  "efficiency_percent": 97.6,
  "input_voltage_range": "120-550V",
  "output_voltage": "220V",
  "phases": 1,
  "mppt_trackers": 2,
  "warranty_years": 10,
  "certifications": ["IEC62109", "IEC61727"],
  "price_brl": 3200.00
}
```

### Deye SUN-8K-SG04LP3-EU

```json
{
  "sku": "INV-DEYE-SUN-8K-SG04LP3-8KW-HYB",
  "manufacturer": "Deye",
  "model": "SUN-8K-SG04LP3-EU",
  "power_rating_kw": 8.0,
  "inverter_type": "HYBRID",
  "efficiency_percent": 97.6,
  "input_voltage_range": "150-850V",
  "output_voltage": "380V",
  "phases": 3,
  "mppt_trackers": 2,
  "warranty_years": 10,
  "battery_compatibility": ["Pylontech", "BYD", "Dyness"],
  "price_brl": 8500.00
}
```

## Critérios de Seleção

### Por Aplicação

**Residencial Standard**
- Grid-tie 3-8kW
- Monofásico ou trifásico
- 2 MPPT trackers
- Eficiência >97%

**Residencial Premium**
- Híbrido 5-15kW
- Compatibilidade com baterias
- WiFi monitoring
- Zero export function

**Comercial**
- Grid-tie 15-50kW
- Trifásico obrigatório
- ≥4 MPPT trackers
- Comunicação RS485/Ethernet

### Por Localização

**Região Nordeste**
- Proteção IP65 mínima
- Temperatura operacional até 60°C
- Certificação INMETRO obrigatória

**Região Sul**
- Proteção contra surtos
- Ampla faixa de tensão
- Eficiência alta em baixa irradiância

## Validação e Testes

### Critérios de Aprovação

1. **Eficiência mínima**: 96% (padrão), 97% (premium)
2. **Garantia mínima**: 5 anos (padrão), 10 anos (premium)
3. **Certificações**: INMETRO, IEC62109, IEC61727
4. **Vida útil**: Mínimo 20 anos

### Processo de Homologação

1. Análise de documentação técnica
2. Teste de laboratório (eficiência, THD, proteções)
3. Teste de campo (6 meses mínimo)
4. Aprovação pela equipe técnica
5. Inclusão no catálogo oficial

## Integração de Sistemas

### Medusa.js

Sincronização automática incluindo:

- Especificações técnicas completas
- Compatibilidade com painéis
- Preços e disponibilidade regional
- Documentação e manuais

### Meta Commerce

Otimização para anúncios:

- Segmentação por tipo de inversor
- Campanhas por faixa de potência
- Retargeting por interesse técnico
- Comparação de especificações

## Tendências Tecnológicas

### 2024-2025

- **Microinversores**: Crescimento em sistemas residenciais
- **Híbridos**: Expansão devido a tarifas
- **Smart Features**: IoT e AI integrados
- **Eficiência**: Meta de 98%+ para premium

### Próximas Tecnologias

- **SiC MOSFETs**: Maior eficiência e densidade
- **AI Optimization**: Otimização automática MPPT
- **Vehicle-to-Grid**: Integração com carros elétricos
- **Blockchain**: Certificação de energia renovável

## Atualizações e Versioning

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para informações técnicas adicionais, consulte o time de engenharia YSH Solar.*