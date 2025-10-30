# Cabos Fotovoltaicos - Padrão SKU YSH

## Visão Geral

Este documento estabelece os padrões de nomenclatura (SKU) para cabos fotovoltaicos utilizados em instalações solares YSH. O padrão contempla diferentes bitolas, tipos e cores de cabos específicos para energia solar.

## Padrão SKU

### Formato

```text
CAB-{GAUGE}MM-{TYPE}-{COLOR}[-{LENGTH}M]
```

### Componentes da SKU

1. **CAB**: Prefixo fixo identificando cabos
2. **GAUGE**: Bitola em mm² (área da seção transversal)
3. **TYPE**: Tipo de cabo (CC, CA, TERRA, FLEX)
4. **COLOR**: Cor do cabo
5. **LENGTH**: Comprimento opcional em metros

### Exemplos

- `CAB-6MM-CC-VERM-50M`
- `CAB-4MM-CC-PRET-25M`
- `CAB-35MM-CA-VERM-100M`

## Bitolas Padrão

### Cabos DC (Corrente Contínua)

| Bitola | Corrente Max | Aplicação | Distância Max |
|--------|--------------|-----------|---------------|
| 4mm² | 35A | Pequenos sistemas | 50m |
| 6mm² | 50A | Residencial padrão | 75m |
| 10mm² | 70A | Comercial pequeno | 100m |
| 16mm² | 105A | Comercial médio | 150m |
| 25mm² | 140A | Comercial grande | 200m |
| 35mm² | 180A | Industrial | 250m |

### Cabos AC (Corrente Alternada)

| Bitola | Corrente Max | Aplicação | Fases |
|--------|--------------|-----------|-------|
| 4mm² | 32A | Monofásico até 7kW | 1F + N + T |
| 6mm² | 41A | Monofásico até 9kW | 1F + N + T |
| 10mm² | 57A | Trifásico até 20kW | 3F + N + T |
| 16mm² | 76A | Trifásico até 30kW | 3F + N + T |
| 25mm² | 101A | Trifásico até 50kW | 3F + N + T |
| 35mm² | 125A | Trifásico até 75kW | 3F + N + T |

## Tipos de Cabos

### CC (DC Solar Cable)

- **Tensão**: 1000V DC / 1500V DC
- **Temperatura**: -40°C a +90°C
- **Aplicação**: String de painéis
- **Características**: Dupla isolação, UV resistente

### CA (AC Power Cable)

- **Tensão**: 600V AC
- **Temperatura**: -10°C a +70°C
- **Aplicação**: Saída do inversor
- **Características**: Flexível, baixa impedância

### TERRA (Grounding Cable)

- **Tensão**: Aterramento
- **Cor**: Verde/amarelo obrigatório
- **Aplicação**: Aterramento de equipamentos
- **Características**: Cobre nu ou isolado

### FLEX (Flexible Multi-conductor)

- **Tensão**: 600V AC/DC
- **Aplicação**: Conexões móveis
- **Características**: Extra flexível, múltiplos condutores

## Cores Padrão

### DC (Corrente Contínua)

| Código | Cor | Polaridade | Aplicação |
|--------|-----|------------|-----------|
| PRET | Preto | Negativo (-) | String negativo |
| VERM | Vermelho | Positivo (+) | String positivo |
| AZUL | Azul | Neutro | Sistemas especiais |

### AC (Corrente Alternada)

| Código | Cor | Fase | Aplicação |
|--------|-----|------|-----------|
| VERM | Vermelho | R/L1 | Fase 1 |
| BRAN | Branco | S/L2 | Fase 2 |
| MARRO | Marrom | T/L3 | Fase 3 |
| AZUL | Azul | N | Neutro |
| VERDE | Verde/Amarelo | PE | Proteção |

### Especiais

| Código | Cor | Aplicação |
|--------|-----|-----------|
| CINZA | Cinza | Comunicação |
| ROXO | Roxo | Monitoramento |

## Especificações Técnicas

### Campos Obrigatórios

- `gauge_mm2`: Bitola em mm²
- `current_rating_a`: Corrente nominal em ampères
- `voltage_rating_v`: Tensão máxima suportada
- `cable_type`: Tipo do cabo
- `conductor_material`: Material do condutor
- `insulation_material`: Material da isolação
- `temperature_range`: Faixa de temperatura operacional
- `uv_resistance`: Resistência UV
- `flame_retardant`: Resistência ao fogo

### Campos Opcionais

- `jacket_material`: Material da capa externa
- `shielding`: Blindagem (se aplicável)
- `flexibility_rating`: Grau de flexibilidade
- `chemical_resistance`: Resistência química
- `crush_resistance`: Resistência ao esmagamento
- `bend_radius_mm`: Raio mínimo de curvatura
- `pulling_tension_n`: Tensão máxima de puxamento
- `certifications`: Certificações aplicáveis

## Construção dos Cabos

### Cabo DC Fotovoltaico

#### Estrutura

1. **Condutor**: Cobre flexível classe 5
2. **Isolação primária**: XLPE (Cross-linked polyethylene)
3. **Capa**: LSOH (Low Smoke Zero Halogen)
4. **Proteção UV**: Estabilizadores UV integrados

#### Especificações

- **Rigidez dielétrica**: 15 kV/mm mínimo
- **Resistência de isolação**: >1000 MΩ.km
- **Vida útil**: 25 anos mínimo
- **Flexibilidade**: -40°C sem rachadura

### Cabo AC Padrão

#### Estrutura

1. **Condutor**: Cobre flexível
2. **Isolação**: PVC ou EPR
3. **Cobertura**: PVC anti-chama
4. **Identificação**: Numeração métrica

#### Especificações

- **Tensão de isolação**: 0,6/1 kV
- **Temperatura máxima**: 70°C (PVC), 90°C (EPR)
- **Resistência mecânica**: Conforme NBR NM 247-3

## Exemplos de Produtos

### Cabo DC 6mm² Vermelho 50m

```json
{
  "sku": "CAB-6MM-CC-VERM-50M",
  "gauge_mm2": 6,
  "current_rating_a": 50,
  "voltage_rating_v": 1500,
  "cable_type": "SOLAR_DC",
  "conductor_material": "Copper",
  "insulation_material": "XLPE",
  "temperature_range": "-40°C to +90°C",
  "uv_resistance": "Excellent",
  "flame_retardant": "LSOH",
  "length_m": 50,
  "color": "Red",
  "certifications": ["TUV", "UL", "IEC"],
  "price_brl": 185.00
}
```

### Cabo AC 35mm² Trifásico 100m

```json
{
  "sku": "CAB-35MM-CA-MULTI-100M",
  "gauge_mm2": 35,
  "current_rating_a": 125,
  "voltage_rating_v": 1000,
  "cable_type": "AC_POWER",
  "conductor_material": "Copper",
  "insulation_material": "EPR",
  "temperature_range": "-10°C to +90°C",
  "cores": 5,
  "length_m": 100,
  "jacket_material": "PVC",
  "price_brl": 2800.00
}
```

## Cálculo de Dimensionamento

### Critério por Corrente

**Fórmula básica**:
```
I_cabo ≥ I_nominal × 1.25
```

**Onde**:
- I_cabo: Corrente máxima do cabo
- I_nominal: Corrente nominal do sistema
- 1.25: Fator de segurança (NBR 5410)

### Critério por Queda de Tensão

**Fórmula DC**:
```
ΔV = (2 × ρ × L × I) / S
```

**Onde**:
- ΔV: Queda de tensão (máx 3%)
- ρ: Resistividade do cobre (0.017 Ω.mm²/m)
- L: Comprimento do cabo (m)
- I: Corrente (A)
- S: Seção do cabo (mm²)

### Exemplo de Cálculo

**Sistema**: 10 painéis de 550W, Isc = 14A  
**String**: 2 strings em paralelo  
**Distância**: 75m até o inversor

**Cálculo**:
- Corrente total: 2 × 14A = 28A
- Corrente com fator: 28A × 1.25 = 35A
- **Cabo mínimo**: 4mm² (35A)

**Verificação queda de tensão**:
- ΔV = (2 × 0.017 × 75 × 28) / 4 = 17.85V
- Em 800V sistema: 17.85/800 = 2.23% ✓

## Instalação e Boas Práticas

### Roteamento de Cabos

#### DC (String)

- Cabos + e - sempre juntos
- Evitar loops longos (EMI)
- Proteção mecânica em bordas
- Fixação a cada 1m máximo

#### AC (Inversor)

- Separação mínima de 30cm dos DC
- Eletrodutos ou canaletas dedicadas
- Aterramento em toda extensão
- Proteção contra roedores

### Conexões

#### Conectores MC4

- Crimpar com ferramenta adequada
- Teste de pull com 100N mínimo
- Vedação IP67 garantida
- Inspeção visual obrigatória

#### Terminais

- Usar terminais apropriados para a bitola
- Crimpar com alicate específico
- Fita isolante 3M ou similar
- Proteção contra umidade

### Proteções

#### Mecânica

- Eletrodutos rígidos em trechos expostos
- Canaletas com tampa em percursos longos
- Proteção anti-UV em trechos aéreos
- Suportes a cada metro

#### Elétrica

- String box com fusíveis
- DPS (protetor de surto) DC e AC
- Disjuntores dimensionados
- Aterramento equipotencial

## Manutenção Preventiva

### Inspeções Visuais

#### Mensal

- Verificar fixações
- Procurar sinais de desgaste
- Check de conectores
- Limpeza de detritos

#### Semestral

- Medição de resistência de isolação
- Teste de conectores MC4
- Verificação de aterramento
- Inspeção termográfica

### Testes Elétricos

#### Anual

- **Resistência de isolação**: >1MΩ entre condutores
- **Continuidade**: <1Ω para todo o percurso
- **Aterramento**: <5Ω resistência total
- **Termografia**: Sem pontos quentes

### Vida Útil e Substituição

#### Indicadores de Degradação

- Ressecamento da capa externa
- Micro fissuras na isolação
- Aquecimento excessivo (>70°C)
- Corrosão nos terminais

#### Critérios de Substituição

- Resistência de isolação <0.5MΩ
- Danos mecânicos visíveis
- Após 20 anos (preventivo)
- Falhas recorrentes

## Normas e Certificações

### Normas Brasileiras

- **NBR 5410**: Instalações elétricas de baixa tensão
- **NBR NM 247-3**: Cabos isolados com PVC
- **NBR 16690**: Instalações elétricas de arranjos fotovoltaicos

### Normas Internacionais

- **IEC 62930**: Cabos DC para aplicações fotovoltaicas
- **UL 4703**: Cabos fotovoltaicos
- **TÜV 2 PfG 1169**: Cabo solar alemão

### Certificações Obrigatórias

- **INMETRO**: Conformidade brasileira
- **TÜV**: Certificação alemã para cabos DC
- **UL**: Certificação americana
- **CE**: Conformidade europeia

## Fornecedores Homologados

### Nacionais

- **Prysmian**: Linha Afumex Solar
- **Nexans**: Cabos fotovoltaicos
- **Furukawa**: Série Solar
- **Condumex**: Sical Enertech

### Importados

- **Lapp**: Ölflex Solar
- **Helukabel**: Helusol
- **TKD**: Cabos premium
- **Belden**: Soluções industriais

## Estoque e Logística

### Gestão de Estoque

#### Comprimentos Padrão

- **25m**: Pequenas instalações
- **50m**: Padrão residencial
- **100m**: Comercial
- **500m**: Industrial (bobinas)

#### Rotatividade

- Cabos DC: Alta rotatividade
- Cabos AC: Média rotatividade
- Bitolas especiais: Sob demanda

### Armazenamento

#### Condições Ideais

- Local seco (<60% umidade)
- Temperatura ambiente (15-25°C)
- Proteção UV total
- Ventilação adequada

#### Manuseio

- Bobinas armazenadas em pé
- Carretéis protegidos de impacto
- Identificação clara e visível
- Controle de lote e validade

## Tendências e Inovações

### 2024-2025

- **Cabos 1500V**: Padrão para sistemas comerciais
- **Materiais avançados**: Isolação XLPO
- **Cabos inteligentes**: Sensores integrados
- **Reciclagem**: Materiais recicláveis

### Tecnologias Emergentes

- **Supercondutores**: Para aplicações especiais
- **Cabos ópticos**: Comunicação integrada
- **Materiais bio**: Isolação biodegradável
- **AI Integration**: Monitoramento preditivo

## Atualizações e Versioning

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para especificações técnicas detalhadas sobre cabeamento, consulte o departamento técnico YSH Solar.*