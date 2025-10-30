# Índice de Padrões SKU YSH Solar

## Visão Geral

Este índice apresenta o sistema completo de padronização de SKUs (Stock Keeping Units) para todos os produtos e componentes utilizados pela YSH Solar. O objetivo é garantir consistência, rastreabilidade e integração eficiente com os sistemas de gestão.

## Estrutura do Sistema

### Categorias de Produtos

| Categoria | Arquivo JSON | Arquivo MD | Status |
|-----------|--------------|------------|--------|
| **Painéis Solares** | `paineis-sku.json` | `paineis-sku.md` | ✅ Completo |
| **Inversores** | `inversores-sku.json` | `inversores-sku.md` | ✅ Completo |
| **Baterias** | `baterias-sku.json` | `baterias-sku.md` | ✅ Completo |
| **Estruturas** | `estruturas-sku.json` | `estruturas-sku.md` | ✅ Completo |
| **Cabos** | `cabos-sku.json` | `cabos-sku.md` | ✅ Completo |
| **Kits Solares** | `kits-sku.json` | `kits-sku.md` | ✅ Completo |

### Localização dos Arquivos

```
data-pipeline/sku-standards/
├── paineis-sku.json           # Dados estruturados painéis
├── paineis-sku.md             # Documentação painéis
├── inversores-sku.json        # Dados estruturados inversores
├── inversores-sku.md          # Documentação inversores
├── baterias-sku.json          # Dados estruturados baterias
├── baterias-sku.md            # Documentação baterias
├── estruturas-sku.json        # Dados estruturados estruturas
├── estruturas-sku.md          # Documentação estruturas
├── cabos-sku.json             # Dados estruturados cabos
├── cabos-sku.md               # Documentação cabos
├── kits-sku.json              # Dados estruturados kits
├── kits-sku.md                # Documentação kits
└── INDEX.md                   # Este arquivo índice
```

## Padrões de Nomenclatura

### Formato Geral

Cada categoria segue um padrão específico de nomenclatura SKU:

```text
{PREFIX}-{MANUFACTURER}-{MODEL}-{SPEC}[-{OPTIONAL}]
```

### Padrões por Categoria

| Categoria | Prefixo | Formato SKU | Exemplo |
|-----------|---------|-------------|---------|
| **Painéis** | PNL | `PNL-{BRAND}-{MODEL}-{POWER}W[-{TECH}]` | `PNL-CANA-CS7N-550MS-550W-MONO` |
| **Inversores** | INV | `INV-{BRAND}-{MODEL}-{POWER}KW[-{TYPE}]` | `INV-GROW-MIN-5000TL-X-5KW-GT` |
| **Baterias** | BAT | `BAT-{BRAND}-{MODEL}-{CAPACITY}KWH-{VOLTAGE}V[-{CHEM}]` | `BAT-BYD-BATTERY-BOX-10.24KWH-256V-LFP` |
| **Estruturas** | EST | `EST-{BRAND}-{ROOF_TYPE}-{CAPACITY}P[-{ORIENT}]` | `EST-SOLG-CER-10P-V` |
| **Cabos** | CAB | `CAB-{GAUGE}MM-{TYPE}-{COLOR}[-{LENGTH}M]` | `CAB-6MM-CC-VERM-50M` |
| **Kits** | KIT | `KIT-{POWER}KWP-{PANEL_BRAND}-{INV_BRAND}[-{TYPE}]` | `KIT-5.5KWP-CANA-GROW-GT` |

## Fabricantes Padronizados

### Códigos de Fabricantes

#### Painéis Solares
- **CANA**: Canadian Solar
- **JINKO**: Jinko Solar  
- **LONGI**: LONGi Solar
- **TRINA**: Trina Solar
- **JA**: JA Solar
- **RISEN**: Risen Energy
- **PHONO**: Phono Solar
- **SOLNP**: Solar N Plus

#### Inversores
- **GROW**: Growatt
- **DEYE**: Deye
- **SOLIS**: Solis
- **GOOD**: GoodWe
- **FRON**: Fronius
- **SMA**: SMA
- **SUNG**: Sungrow
- **HUAW**: Huawei

#### Baterias
- **BYD**: BYD
- **PYLON**: Pylontech
- **FRLM**: Freedom Won
- **DYNS**: Dyness
- **LG**: LG Energy
- **TESLA**: Tesla

#### Estruturas
- **SOLG**: Solar Group
- **ROMA**: Romagnole
- **KRNN**: K2 Systems
- **ALDO**: Aldo Solar
- **SCHL**: Schletter
- **CLEN**: Clenergy

## Especificações Técnicas

### Campos Padrão por Categoria

#### Todos os Produtos
- `manufacturer`: Fabricante
- `model`: Modelo específico
- `warranty_years`: Garantia em anos
- `price_brl`: Preço em reais brasileiros
- `certifications`: Certificações aplicáveis

#### Painéis Solares
- `power_rating_w`: Potência em Watts
- `efficiency_percent`: Eficiência do módulo
- `cell_technology`: Tecnologia das células
- `dimensions_mm`: Dimensões físicas
- `weight_kg`: Peso em quilogramas

#### Inversores
- `power_rating_kw`: Potência em kW
- `efficiency_percent`: Eficiência máxima
- `inverter_type`: Tipo (Grid-tie, Híbrido, etc.)
- `phases`: Número de fases
- `mppt_trackers`: Número de rastreadores MPPT

#### Baterias
- `usable_capacity_kwh`: Capacidade útil em kWh
- `nominal_voltage_v`: Tensão nominal
- `chemistry`: Tecnologia química
- `cycle_life`: Ciclos de vida
- `dod_percent`: Profundidade de descarga

#### Estruturas
- `roof_type`: Tipo de telhado
- `panel_capacity`: Número de painéis
- `orientation`: Orientação dos painéis
- `wind_load_pa`: Carga de vento suportada
- `material`: Material principal

#### Cabos
- `gauge_mm2`: Bitola em mm²
- `current_rating_a`: Corrente nominal
- `voltage_rating_v`: Tensão máxima
- `cable_type`: Tipo do cabo
- `temperature_range`: Faixa de temperatura

#### Kits
- `total_power_kwp`: Potência total do kit
- `kit_type`: Tipo do kit
- `estimated_generation_kwh_month`: Geração estimada
- `payback_period_months`: Período de retorno

## Integração com Sistemas

### Medusa.js E-commerce

Os padrões SKU são automaticamente sincronizados com o sistema Medusa.js para:

- **Catálogo de produtos**: Listagem organizada
- **Carrinho de compras**: Identificação única
- **Gestão de estoque**: Controle de inventário
- **Preços dinâmicos**: Atualização automática
- **Categorização**: Organização hierárquica

### Meta Commerce Platform

Integração completa para marketing digital:

- **Facebook Catalog**: Feed automático de produtos
- **Google Merchant**: Listagem no Google Shopping
- **Anúncios dinâmicos**: Retargeting por categoria
- **Comparação**: Especificações técnicas
- **Conversão**: Otimização de campanhas

### Sistema ERP

Conexão com sistemas de gestão empresarial:

- **Compras**: Códigos para fornecedores
- **Estoque**: Controle de movimentação
- **Vendas**: Identificação em pedidos
- **Financeiro**: Precificação e custos
- **Produção**: Lista de materiais (BOM)

## Validação e Conformidade

### Critérios de Validação

#### Formato SKU
- Regex pattern específico por categoria
- Códigos de fabricante válidos
- Especificações dentro das faixas permitidas
- Campos obrigatórios preenchidos

#### Técnica
- Certificações necessárias presentes
- Especificações dentro dos padrões
- Compatibilidade entre componentes
- Normas brasileiras atendidas

#### Comercial
- Preços dentro da faixa de mercado
- Disponibilidade confirmada
- Margem adequada
- Aprovação do comitê técnico

### Processo de Aprovação

1. **Submissão**: Proposta de novo produto/SKU
2. **Validação técnica**: Verificação de especificações
3. **Teste de compatibilidade**: Integração com outros componentes
4. **Aprovação comercial**: Análise de viabilidade
5. **Inclusão**: Adição ao catálogo oficial

## Manutenção e Atualizações

### Ciclo de Revisões

#### Mensal
- Atualização de preços
- Novos produtos de fabricantes existentes
- Correções de especificações
- Sincronização com sistemas

#### Trimestral
- Novos fabricantes
- Categorias emergentes
- Revisão de padrões
- Otimização de processos

#### Anual
- Revisão completa dos padrões
- Atualização de normas
- Migração de versões
- Treinamento de equipes

### Controle de Versão

- **Major (X.0.0)**: Mudanças no formato SKU
- **Minor (0.X.0)**: Novos fabricantes ou categorias
- **Patch (0.0.X)**: Correções e atualizações

**Versão Atual**: 2.0.0  
**Data**: 19 de outubro de 2024

## Equipe Responsável

### Gestão Técnica
- **Engenharia**: Validação técnica e especificações
- **Qualidade**: Certificações e conformidade
- **P&D**: Novas tecnologias e tendências

### Gestão Comercial
- **Produtos**: Definição de mix e preços
- **Compras**: Negociação com fornecedores
- **Vendas**: Feedback de mercado

### Gestão de TI
- **Desenvolvimento**: Integração com sistemas
- **Dados**: Sincronização e qualidade
- **Infraestrutura**: Performance e disponibilidade

## Contato e Suporte

### Para Dúvidas Técnicas
- **Email**: engenharia@ysh.solar
- **Teams**: Canal #sku-standards
- **Documentação**: Confluence YSH

### Para Novos Produtos
- **Email**: produtos@ysh.solar
- **Sistema**: Portal de submissão
- **Processo**: Workflow de aprovação

### Para Integração de Sistemas
- **Email**: ti@ysh.solar
- **API**: Documentação técnica
- **Suporte**: 24/7 para sistemas críticos

---

*Este documento é mantido pela equipe de Produtos YSH Solar e atualizado conforme necessário para refletir as melhores práticas do setor.*