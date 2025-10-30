# Estruturas de Fixação - Padrão SKU YSH

## Visão Geral

Este documento estabelece os padrões de nomenclatura (SKU) para estruturas de fixação de painéis solares utilizadas em projetos YSH Solar. O padrão contempla diferentes tipos de telhados e orientações de instalação.

## Padrão SKU

### Formato

```text
EST-{MANUFACTURER}-{ROOF_TYPE}-{CAPACITY}P[-{ORIENTATION}]
```

### Componentes da SKU

1. **EST**: Prefixo fixo identificando estruturas
2. **MANUFACTURER**: Código de 3-5 letras do fabricante
3. **ROOF_TYPE**: Tipo de telhado/aplicação
4. **CAPACITY**: Número de painéis suportados
5. **ORIENTATION**: Orientação opcional (V, H, INC, BAL)

### Exemplos

- `EST-SOLG-CER-10P-V`
- `EST-ROMA-MET-15P-H`
- `EST-KRNN-SOLO-20P-INC`

## Fabricantes Aprovados

### Tier 1 (Nacional)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| SOLG | Solar Group | Brasil | Cerâmico, Metálico |
| ROMA | Romagnole | Brasil | Todos os tipos |
| ALDO | Aldo Solar | Brasil | Residencial |

### Tier 2 (Internacional)

| Código | Fabricante | País | Especialidade |
|--------|------------|------|---------------|
| KRNN | K2 Systems | Alemanha | Premium, Comercial |
| SCHL | Schletter | Alemanha | Industrial |
| CLEN | Clenergy | Austrália | Solo, Tracking |

## Tipos de Telhado

### CER (Cerâmico)

- **Descrição**: Telhas cerâmicas tradicionais
- **Fixação**: Ganchos específicos por tipo de telha
- **Aplicação**: Residencial brasileiro
- **Características**: Vedação garantida, estética

### MET (Metálico)

- **Descrição**: Telhas metálicas trapezoidais
- **Fixação**: Parafusos auto-atarraxantes
- **Aplicação**: Industrial, comercial
- **Características**: Instalação rápida, resistente

### FIB (Fibrocimento)

- **Descrição**: Telhas de fibrocimento onduladas
- **Fixação**: Parafusos com vedação
- **Aplicação**: Galpões, industrial
- **Características**: Econômica, durável

### LAJE (Concreto)

- **Descrição**: Laje de concreto plana
- **Fixação**: Chumbadores ou lastro
- **Aplicação**: Comercial, residencial
- **Características**: Estrutural, versátil

### SOLO (Solo)

- **Descrição**: Montagem no solo
- **Fixação**: Fundação de concreto
- **Aplicação**: Usinas, grandes áreas
- **Características**: Orientação otimizada

## Orientações

### V (Vertical/Portrait)

- **Descrição**: Painéis na posição vertical
- **Vantagem**: Menor área de instalação
- **Aplicação**: Espaços limitados
- **Considerações**: Maior sombreamento entre fileiras

### H (Horizontal/Landscape)

- **Descrição**: Painéis na posição horizontal
- **Vantagem**: Melhor aproveitamento vento
- **Aplicação**: Áreas amplas
- **Considerações**: Maior área necessária

### INC (Inclinado)

- **Descrição**: Ângulo otimizado para latitude
- **Vantagem**: Máxima geração anual
- **Aplicação**: Solo, laje plana
- **Considerações**: Estrutura mais complexa

### BAL (Lastrado)

- **Descrição**: Fixação por peso, sem furação
- **Vantagem**: Não compromete impermeabilização
- **Aplicação**: Lajes, telhados planos
- **Considerações**: Carga adicional

### 2E (Dois Eixos)

- **Descrição**: Rastreamento solar automático
- **Vantagem**: +25% geração vs fixo
- **Aplicação**: Usinas, alta irradiação
- **Considerações**: Manutenção, custo

## Especificações Técnicas

### Campos Obrigatórios

- `manufacturer`: Fabricante da estrutura
- `roof_type`: Tipo de telhado/aplicação
- `panel_capacity`: Número de painéis
- `orientation`: Orientação dos painéis
- `material`: Material principal
- `wind_load_pa`: Carga de vento suportada
- `snow_load_pa`: Carga de neve/sobrecarga
- `tilt_angle_degrees`: Ângulo de inclinação
- `warranty_years`: Garantia em anos

### Campos Opcionais

- `panel_size_compatibility`: Tamanhos de painéis compatíveis
- `installation_time_hours`: Tempo estimado de instalação
- `weight_kg`: Peso total da estrutura
- `corrosion_protection`: Proteção contra corrosão
- `certifications`: Certificações estruturais
- `components_list`: Lista detalhada de componentes
- `tools_required`: Ferramentas necessárias
- `installation_complexity`: Nível de complexidade

## Cargas Estruturais

### Cargas de Vento

#### Região I (Até 30 m/s)

- **Carga mínima**: 1500 Pa
- **Aplicação**: Interior, áreas protegidas
- **Estrutura**: Standard

#### Região II (30-35 m/s)

- **Carga mínima**: 2000 Pa
- **Aplicação**: Maioria do Brasil
- **Estrutura**: Reforçada

#### Região III (35-40 m/s)

- **Carga mínima**: 2500 Pa
- **Aplicação**: Litoral, áreas expostas
- **Estrutura**: Heavy duty

#### Região IV (40+ m/s)

- **Carga mínima**: 3000 Pa
- **Aplicação**: Offshore, montanhas
- **Estrutura**: Ultra resistente

### Cargas de Neve/Sobrecarga

- **Padrão**: 800 Pa (mínimo NBR)
- **Reforçado**: 1200 Pa (segurança extra)
- **Heavy duty**: 1600 Pa (cargas extremas)

## Materiais e Proteção

### Alumínio

- **Vantagens**: Leve, resistente à corrosão
- **Aplicação**: Residencial, comercial
- **Proteção**: Anodização ou pintura
- **Vida útil**: 25+ anos

### Aço Galvanizado

- **Vantagens**: Resistente, econômico
- **Aplicação**: Industrial, utility
- **Proteção**: Galvanização a quente
- **Vida útil**: 20+ anos

### Aço Inoxidável

- **Vantagens**: Máxima resistência à corrosão
- **Aplicação**: Marinha, industrial pesada
- **Proteção**: Natural
- **Vida útil**: 30+ anos

## Exemplos de Produtos

### Solar Group Cerâmico 10P Vertical

```json
{
  "sku": "EST-SOLG-CER-10P-V",
  "manufacturer": "Solar Group",
  "roof_type": "CERAMIC",
  "panel_capacity": 10,
  "orientation": "VERTICAL",
  "material": "Aluminum",
  "wind_load_pa": 2000,
  "snow_load_pa": 800,
  "tilt_angle_degrees": 10,
  "warranty_years": 12,
  "installation_time_hours": 4,
  "weight_kg": 85,
  "corrosion_protection": "Anodized",
  "price_brl": 1200.00,
  "components_list": [
    "10x Gancho telha cerâmica",
    "5x Trilho 4000mm",
    "20x Grampo intermediário",
    "4x Grampo terminal",
    "Parafusos e acessórios"
  ]
}
```

### Romagnole Metálico 15P Horizontal

```json
{
  "sku": "EST-ROMA-MET-15P-H",
  "manufacturer": "Romagnole",
  "roof_type": "METALLIC",
  "panel_capacity": 15,
  "orientation": "HORIZONTAL",
  "material": "Aluminum",
  "wind_load_pa": 2500,
  "snow_load_pa": 1000,
  "tilt_angle_degrees": 5,
  "warranty_years": 15,
  "installation_time_hours": 3,
  "weight_kg": 95,
  "corrosion_protection": "Anodized + Paint",
  "price_brl": 1650.00,
  "installation_complexity": "Medium"
}
```

## Critérios de Seleção

### Por Tipo de Telhado

#### Cerâmico

- Verificar tipo específico de telha
- Ganchos adequados para cada modelo
- Atenção à vedação
- Estrutura do telhado

#### Metálico

- Verificar perfil da telha
- Parafusos apropriados
- Vedação com EPDM
- Dilatação térmica

#### Fibrocimento

- Estado das telhas (amianto?)
- Capacidade estrutural
- Parafusos inox obrigatório
- Vedação reforçada

### Por Região

#### Região Nordeste

- Proteção UV extra
- Materiais claros (menor temperatura)
- Ventilação adequada
- Resistência à salinidade (litoral)

#### Região Sul

- Cargas de neve/granizo
- Resistência a ventos fortes
- Materiais que suportem ciclagem térmica
- Drenagem adequada

## Instalação e Manutenção

### Ferramentas Necessárias

#### Básicas

- Furadeira com brocas específicas
- Parafusadeira
- Chaves Allen e Phillips
- Nível a laser
- Trena

#### Avançadas

- Morsa para trilhos
- Alicate desencapador
- Multímetro
- Torquímetro
- Equipamentos de segurança

### Sequência de Instalação

1. **Planejamento**: Layout e marcação
2. **Fixação**: Ganchos/suportes primários
3. **Trilhos**: Instalação dos trilhos
4. **Nivelamento**: Ajuste e alinhamento
5. **Grampos**: Fixação dos grampos
6. **Painéis**: Montagem dos painéis
7. **Aterramento**: Conexão do aterramento
8. **Inspeção**: Verificação final

### Manutenção Preventiva

#### Anual

- Inspeção visual de componentes
- Verificação de fixações
- Limpeza de detritos
- Check de aterramento

#### Quinquenal

- Torque de parafusos
- Verificação de corrosão
- Troca de vedações se necessário
- Inspeção estrutural detalhada

## Normas e Certificações

### Normas Brasileiras

- **NBR 6123**: Forças devido ao vento
- **NBR 8800**: Estruturas de aço
- **NBR 6120**: Cargas para cálculo de estruturas
- **NBR 14762**: Estruturas de aço formadas a frio

### Certificações Internacionais

- **IEC 61730**: Qualificação de segurança
- **UL 2703**: Sistemas de montagem
- **TÜV**: Certificação alemã
- **CE**: Conformidade europeia

## Tendências e Inovações

### 2024-2025

- **Instalação mais rápida**: Sistemas plug & play
- **Materiais avançados**: Composites, polímeros
- **Integração**: BIPV (Building Integrated PV)
- **Automação**: Robôs de instalação

### Tecnologias Emergentes

- **Estruturas flutuantes**: Para hidrelétricas
- **Agrovoltaico**: Painéis + agricultura
- **Estruturas adaptáveis**: Ângulo variável
- **Materiais inteligentes**: Auto-limpeza, auto-reparo

## Atualizações e Versioning

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para projetos estruturais específicos, consulte o departamento de engenharia YSH Solar.*