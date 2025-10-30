# Baterias - Padrão SKU YSH

## Visão Geral

Este documento define os padrões de nomenclatura (SKU) para sistemas de armazenamento de energia (baterias) utilizados em projetos solares YSH. O padrão abrange diferentes tecnologias de baterias e classes de voltagem.

## Padrão SKU

### Formato

```text
BAT-{MANUFACTURER}-{MODEL}-{CAPACITY}KWH-{VOLTAGE}V[-{CHEMISTRY}]
```

### Componentes da SKU

1. **BAT**: Prefixo fixo identificando baterias
2. **MANUFACTURER**: Código de 3-5 letras do fabricante
3. **MODEL**: Modelo específico da bateria
4. **CAPACITY**: Capacidade útil em kWh
5. **VOLTAGE**: Tensão nominal do sistema
6. **CHEMISTRY**: Tecnologia química opcional

### Exemplos

- `BAT-BYD-BATTERY-BOX-10.24KWH-256V-LFP`
- `BAT-PYLON-US2000B-PLUS-2.4KWH-48V-LFP`
- `BAT-FRLM-LITE-HOME-5.12KWH-51V-LFP`

## Fabricantes Aprovados

### Tier 1 (Premium)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| BYD | BYD | China | LFP Premium, Utility |
| PYLON | Pylontech | China | Residential, Commercial |
| FRLM | Freedom Won | África do Sul | Sistemas híbridos |
| DYNS | Dyness | China | Modular, Escalável |

### Tier 2 (Performance)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| HUAW | Huawei | China | Smart Energy |
| LG | LG Energy | Coreia do Sul | ESS Comercial |
| TESLA | Tesla | EUA | Powerwall, Megapack |

## Tecnologias Químicas

### LFP (Lithium Iron Phosphate)

- **Ciclos**: 6000-8000 (80% DOD)
- **Segurança**: Muito alta
- **Custo**: Médio-baixo
- **Aplicação**: Residencial, comercial
- **Temperatura**: -10°C a +55°C

### NMC (Nickel Manganese Cobalt)

- **Ciclos**: 3000-5000 (80% DOD)
- **Densidade**: Alta
- **Custo**: Médio-alto
- **Aplicação**: Veículos elétricos, portátil
- **Temperatura**: 0°C a +45°C

### NCA (Nickel Cobalt Aluminum)

- **Ciclos**: 2000-3000 (80% DOD)
- **Densidade**: Muito alta
- **Custo**: Alto
- **Aplicação**: Premium, aerospace
- **Temperatura**: 5°C a +40°C

### LTO (Lithium Titanate Oxide)

- **Ciclos**: 15000+ (100% DOD)
- **Velocidade**: Carga ultra-rápida
- **Custo**: Muito alto
- **Aplicação**: Industrial, UPS
- **Temperatura**: -30°C a +60°C

## Classes de Voltagem

### Low Voltage (12-48V)

- **Aplicação**: RV, Marine, Backup residencial
- **Capacidade**: 1-20kWh
- **Características**: Plug & play, segurança

### Standard Voltage (48-100V)

- **Aplicação**: Residencial padrão
- **Capacidade**: 2-50kWh
- **Características**: Expansível, eficiente

### High Voltage (100-600V)

- **Aplicação**: Comercial, industrial
- **Capacidade**: 20-200kWh
- **Características**: Alta eficiência, menor corrente

### Ultra High Voltage (600V+)

- **Aplicação**: Utility scale, grid storage
- **Capacidade**: 100kWh+
- **Características**: Máxima eficiência

## Especificações Técnicas

### Campos Obrigatórios

- `manufacturer`: Fabricante da bateria
- `model`: Modelo específico
- `usable_capacity_kwh`: Capacidade útil em kWh
- `nominal_voltage_v`: Tensão nominal
- `chemistry`: Tecnologia química
- `cycle_life`: Ciclos de vida esperados
- `dod_percent`: Profundidade de descarga
- `round_trip_efficiency`: Eficiência round-trip
- `warranty_years`: Garantia em anos

### Campos Opcionais

- `total_capacity_kwh`: Capacidade total instalada
- `max_charge_current`: Corrente máxima de carga
- `max_discharge_current`: Corrente máxima de descarga
- `operating_temp_range`: Faixa de temperatura
- `storage_temp_range`: Temperatura de armazenamento
- `ip_rating`: Grau de proteção
- `weight_kg`: Peso total do sistema
- `dimensions_mm`: Dimensões físicas
- `communication_protocol`: Protocolo de comunicação
- `parallel_capacity`: Número máximo em paralelo

## Faixas de Capacidade

### Residencial (2-20kWh)

- **Pequeno**: 2-5kWh (backup essencial)
- **Médio**: 5-10kWh (backup parcial)
- **Grande**: 10-20kWh (backup total)

### Comercial (20-200kWh)

- **PME**: 20-50kWh (horário de ponta)
- **Médio**: 50-100kWh (shift de carga)
- **Grande**: 100-200kWh (arbitragem)

### Industrial (200kWh+)

- **Grid Support**: 200-500kWh
- **Utility Scale**: 500kWh+
- **Microgrids**: Customizado

## Exemplos de Produtos

### BYD Battery-Box Premium LVS

```json
{
  "sku": "BAT-BYD-BATTERY-BOX-10.24KWH-256V-LFP",
  "manufacturer": "BYD",
  "model": "Battery-Box Premium LVS",
  "usable_capacity_kwh": 10.24,
  "total_capacity_kwh": 11.52,
  "nominal_voltage_v": 256,
  "chemistry": "LFP",
  "cycle_life": 6000,
  "dod_percent": 90,
  "round_trip_efficiency": 96.5,
  "warranty_years": 10,
  "operating_temp_range": "-10°C to +50°C",
  "communication_protocol": "CAN",
  "price_brl": 18500.00
}
```

### Pylontech US2000B Plus

```json
{
  "sku": "BAT-PYLON-US2000B-PLUS-2.4KWH-48V-LFP",
  "manufacturer": "Pylontech",
  "model": "US2000B Plus",
  "usable_capacity_kwh": 2.4,
  "total_capacity_kwh": 2.56,
  "nominal_voltage_v": 48,
  "chemistry": "LFP",
  "cycle_life": 6000,
  "dod_percent": 95,
  "round_trip_efficiency": 95.0,
  "warranty_years": 10,
  "parallel_capacity": 16,
  "weight_kg": 24.0,
  "price_brl": 4200.00
}
```

## Critérios de Seleção

### Por Aplicação

#### Backup Residencial

- Capacidade: 5-15kWh
- Tecnologia: LFP preferencial
- Voltagem: 48V padrão
- Ciclos: 6000+ mínimo

#### Arbitragem Comercial

- Capacidade: 50-200kWh
- Tecnologia: LFP ou NMC
- Voltagem: 400V+ preferencial
- Eficiência: >95% round-trip

#### Off-Grid Rural

- Capacidade: 10-50kWh
- Tecnologia: LFP obrigatória
- Temperatura: Ampla faixa
- Manutenção: Baixa/zero

### Por Região

#### Região Norte/Nordeste

- Temperatura alta: LFP preferencial
- Umidade: IP54+ obrigatório
- Ventilação: Ativa recomendada

#### Região Sul

- Temperatura baixa: Aquecimento interno
- Ventilação: Natural possível
- Instalação: Indoor/outdoor

## Integração de Sistemas

### Compatibilidade com Inversores

#### Growatt

- Pylontech: CAN nativo
- BYD: CAN com protocolo específico
- Dyness: RS485/CAN

#### Deye

- Pylontech: CAN plug & play
- BYD: Protocolo nativo
- Freedom Won: CAN configurado

#### Solis

- Pylontech: CAN padrão
- BYD: Protocolo específico
- Configuração manual para outros

### Monitoramento

#### Sistemas Integrados

- App do fabricante
- Portal web dedicado
- Alertas por email/SMS
- Histórico de performance

#### Plataformas Terceiras

- Home Assistant
- Solar Assistant
- Victron VRM
- APIs customizadas

## Segurança e Certificações

### Certificações Obrigatórias

- **IEC62619**: Segurança de baterias Li-ion
- **UL1973**: Sistemas de energia estacionária
- **IEC61427**: Aplicações gerais
- **CE**: Conformidade europeia

### Sistemas de Proteção

#### BMS (Battery Management System)

- Sobretensão/subtensão
- Sobrecorrente de carga/descarga
- Temperatura alta/baixa
- Balanceamento de células

#### Proteções Externas

- Fusíveis/disjuntores
- Supressores de surto
- Isolamento galvânico
- Sistema de incêndio

## Manutenção e Operação

### Rotina Preventiva

#### Mensal

- Verificação visual de conexões
- Limpeza de terminais
- Check de temperatura ambiente
- Teste de comunicação

#### Trimestral

- Análise de performance
- Verificação de balanço
- Teste de alarmes
- Atualização de firmware

#### Anual

- Teste de capacidade
- Calibração de SOC
- Verificação de isolamento
- Revisão completa do sistema

### Indicadores de Performance

- **SOH** (State of Health): >80% após 10 anos
- **Eficiência**: Deve manter >90% da especificação
- **Balanceamento**: Delta <50mV entre células
- **Temperatura**: Dentro da faixa especificada

## Tendências e Futuro

### 2024-2025

- **LFP Dominance**: 80%+ do mercado residencial
- **HV Systems**: Crescimento em comercial
- **Smart Features**: AI para otimização
- **Vehicle-to-Grid**: Integração com EVs

### Tecnologias Emergentes

- **Sodium-ion**: Alternativa ao lítio
- **Solid-state**: Próxima geração
- **Flow batteries**: Longa duração
- **Hydrogen**: Armazenamento sazonal

## Atualizações e Versioning

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para suporte técnico sobre sistemas de armazenamento, contacte a equipe de energia YSH Solar.*