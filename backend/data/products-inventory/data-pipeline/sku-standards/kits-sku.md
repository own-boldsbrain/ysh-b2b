# Kits Solares - Padrão SKU YSH

## Visão Geral

Este documento estabelece os padrões de nomenclatura (SKU) para kits solares completos oferecidos pela YSH Solar. Os kits representam soluções integradas que incluem todos os componentes necessários para uma instalação fotovoltaica.

## Padrão SKU

### Formato

```text
KIT-{POWER}KWP-{PANEL_BRAND}-{INVERTER_BRAND}[-{TYPE}]
```

### Componentes da SKU

1. **KIT**: Prefixo fixo identificando kits completos
2. **POWER**: Potência total do kit em kWp
3. **PANEL_BRAND**: Marca dos painéis solares
4. **INVERTER_BRAND**: Marca do inversor
5. **TYPE**: Tipo opcional (GT, HYB, OG, MICRO)

### Exemplos

- `KIT-5.5KWP-CANA-GROW-GT`
- `KIT-8.8KWP-JINKO-DEYE-HYB`
- `KIT-1.14KWP-SOLNP-DEYE-MICRO`

## Tipos de Kits

### Grid-Tie (GT)

- **Descrição**: Conectado à rede sem backup
- **Componentes**: Painéis + Inversor Grid-Tie + Estrutura + Cabos + String Box
- **Aplicação**: Redução de conta de luz
- **Características**: Menor custo, instalação simples

### Híbrido (HYB)

- **Descrição**: Conectado à rede com backup de bateria
- **Componentes**: Painéis + Inversor Híbrido + Baterias + Estrutura + Cabos
- **Aplicação**: Backup de energia + economia
- **Características**: Autonomia parcial, gestão inteligente

### Off-Grid (OG)

- **Descrição**: Sistema isolado da rede elétrica
- **Componentes**: Painéis + Controlador + Inversor + Baterias + Estrutura
- **Aplicação**: Locais remotos, autonomia total
- **Características**: Independência energética

### Microinversores (MICRO)

- **Descrição**: Inversores individuais por painel
- **Componentes**: Painéis + Microinversores + Estrutura + Cabos
- **Aplicação**: Sistemas com sombreamento
- **Características**: Otimização individual, monitoramento

## Faixas de Potência

### Residencial (1-15kWp)

#### Entry Level (1-3kWp)

- **Público**: Primeiros compradores
- **Objetivo**: Redução parcial da conta
- **Características**: Baixo investimento, rápido payback

#### Standard (3-8kWp)

- **Público**: Famílias médias
- **Objetivo**: Zerar conta de luz
- **Características**: Melhor custo-benefício

#### Premium (8-15kWp)

- **Público**: Famílias grandes, alto consumo
- **Objetivo**: Geração excedente
- **Características**: Máximo aproveitamento

### Comercial (15-100kWp)

#### Pequeno Comércio (15-30kWp)

- **Público**: Lojas, escritórios
- **Objetivo**: Redução de custos operacionais
- **Características**: ROI atrativo

#### Médio Comércio (30-75kWp)

- **Público**: Indústrias leves, supermercados
- **Objetivo**: Gestão de demanda
- **Características**: Monitoramento avançado

#### Grande Comércio (75-100kWp)

- **Público**: Grandes indústrias
- **Objetivo**: Sustentabilidade + economia
- **Características**: Sistemas robustos

### Industrial (100kWp+)

- **Aplicação**: Usinas, grandes complexos
- **Objetivo**: Geração distribuída
- **Características**: Projeto customizado

## Composição Padrão dos Kits

### Kit Grid-Tie Padrão

| Componente | Percentual | Descrição |
|------------|------------|-----------|
| Painéis | 65% | Módulos fotovoltaicos |
| Inversor | 20% | Inversor grid-tie |
| Estrutura | 8% | Sistema de fixação |
| Elétricos | 4% | Cabos, conectores, string box |
| Instalação | 3% | Materiais de instalação |

### Kit Híbrido Padrão

| Componente | Percentual | Descrição |
|------------|------------|-----------|
| Painéis | 45% | Módulos fotovoltaicos |
| Baterias | 30% | Sistema de armazenamento |
| Inversor | 15% | Inversor híbrido |
| Estrutura | 6% | Sistema de fixação |
| Elétricos | 4% | Cabos, conectores |

## Especificações Técnicas

### Campos Obrigatórios

- `total_power_kwp`: Potência total do kit
- `panel_brand`: Marca dos painéis
- `panel_model`: Modelo dos painéis
- `panel_quantity`: Quantidade de painéis
- `inverter_brand`: Marca do inversor
- `inverter_model`: Modelo do inverter
- `kit_type`: Tipo do kit
- `estimated_generation_kwh_month`: Geração estimada mensal
- `payback_period_months`: Período de retorno

### Campos Opcionais

- `battery_brand`: Marca da bateria (se aplicável)
- `battery_capacity_kwh`: Capacidade da bateria
- `structure_type`: Tipo de estrutura
- `roof_type`: Tipo de telhado
- `installation_area_m2`: Área necessária
- `backup_time_hours`: Tempo de backup
- `co2_savings_kg_year`: Economia de CO₂ anual

## Critérios de Composição

### Seleção de Componentes

#### Painéis

- **Eficiência**: Mínimo 20% para residencial
- **Garantia**: 25 anos de performance
- **Tier**: Apenas Tier 1 para kits premium

#### Inversores

- **Eficiência**: Mínimo 97% europeia
- **Garantia**: Mínimo 10 anos
- **Compatibilidade**: 100% com painéis selecionados

#### Ratio Painel/Inversor

- **Grid-tie**: 1.0 - 1.3 (otimizado para máxima geração)
- **Híbrido**: 0.8 - 1.2 (balanceado carga/bateria)
- **Off-grid**: 1.5 - 2.0 (margem para autonomia)

### Validação de Compatibilidade

#### Elétrica

- Tensão de operação dentro da faixa do inversor
- Corrente de string adequada
- Proteções dimensionadas corretamente

#### Mecânica

- Estrutura compatível com tipo de telhado
- Peso total dentro dos limites estruturais
- Área disponível suficiente

## Exemplos de Kits

### Kit Entry Level - 1.14kWp

```json
{
  "sku": "KIT-1.14KWP-SOLNP-DEYE-MICRO",
  "total_power_kwp": 1.14,
  "panel_brand": "Solar N Plus",
  "panel_model": "570W N-Type",
  "panel_quantity": 2,
  "inverter_brand": "Deye",
  "inverter_model": "SUN-M225G4-EU-Q0",
  "kit_type": "MICROINVERTER",
  "estimated_generation_kwh_month": 171,
  "installation_area_m2": 6,
  "payback_period_months": 45,
  "price_brl": 2950.00,
  "target_audience": "Primeiros compradores"
}
```

### Kit Standard - 5.5kWp

```json
{
  "sku": "KIT-5.5KWP-CANA-GROW-GT", 
  "total_power_kwp": 5.5,
  "panel_brand": "Canadian Solar",
  "panel_model": "CS7N-550MS",
  "panel_quantity": 10,
  "inverter_brand": "Growatt",
  "inverter_model": "MIN 5000TL-X",
  "kit_type": "GRID_TIE",
  "estimated_generation_kwh_month": 825,
  "installation_area_m2": 28,
  "payback_period_months": 48,
  "price_brl": 15500.00,
  "target_audience": "Residencial padrão"
}
```

### Kit Premium Híbrido - 8.8kWp

```json
{
  "sku": "KIT-8.8KWP-JINKO-DEYE-HYB",
  "total_power_kwp": 8.8,
  "panel_brand": "Jinko Solar",
  "panel_model": "Tiger Neo 550W",
  "panel_quantity": 16,
  "inverter_brand": "Deye", 
  "inverter_model": "SUN-8K-SG04LP3-EU",
  "kit_type": "HYBRID",
  "battery_brand": "Pylontech",
  "battery_capacity_kwh": 10.24,
  "estimated_generation_kwh_month": 1320,
  "backup_time_hours": 8,
  "payback_period_months": 52,
  "price_brl": 42500.00,
  "target_audience": "Premium com backup"
}
```

## Processo de Criação de Kits

### Análise de Mercado

1. **Pesquisa de demanda**: Potências mais procuradas
2. **Análise de preços**: Faixas competitivas
3. **Tendências**: Tecnologias emergentes
4. **Sazonalidade**: Variações de demanda

### Seleção de Componentes

1. **Disponibilidade**: Estoque garantido
2. **Preço**: Margem adequada
3. **Qualidade**: Padrões YSH
4. **Compatibilidade**: Teste completo

### Validação Técnica

1. **Simulação**: Performance esperada
2. **Teste de bancada**: Compatibilidade
3. **Instalação piloto**: Validação real
4. **Aprovação**: Comitê técnico

### Precificação

1. **Custo total**: Soma dos componentes
2. **Margem**: Padrão por categoria
3. **Competitividade**: Análise de mercado
4. **Flexibilidade**: Descontos possíveis

## Marketing e Vendas

### Segmentação

#### Por Investimento

- **Econômico**: R$ 2.000 - R$ 8.000
- **Padrão**: R$ 8.000 - R$ 25.000
- **Premium**: R$ 25.000 - R$ 60.000
- **Comercial**: R$ 60.000+

#### Por Aplicação

- **Economia básica**: 30-50% redução conta
- **Zero conta**: 95-100% redução
- **Geração excedente**: >100% do consumo
- **Backup crítico**: Sistemas híbridos

### Estratégias de Venda

#### Consultiva

1. **Análise de consumo**: Histórico 12 meses
2. **Dimensionamento**: Kit adequado
3. **Projeção financeira**: ROI e payback
4. **Proposta técnica**: Especificações completas

#### Digital

1. **Configurador online**: Self-service
2. **Comparação**: Diferentes opções
3. **Simulação**: Geração e economia
4. **Checkout**: Compra direta

## Garantias e Suporte

### Garantia dos Kits

#### Componentes

- **Painéis**: 25 anos performance
- **Inversores**: 10-12 anos produto
- **Estruturas**: 12-15 anos
- **Instalação**: 5 anos serviço

#### Sistema Completo

- **Performance**: Garantia de geração
- **Integração**: Compatibilidade garantida
- **Suporte**: Help desk técnico
- **Peças**: Reposição garantida

### Serviços Inclusos

#### Pré-venda

- Análise técnica
- Dimensionamento
- Simulação financeira
- Projeto básico

#### Pós-venda

- Instalação profissional
- Comissionamento
- Treinamento do usuário
- Suporte técnico

## Logística e Entrega

### Embalagem

#### Padronização

- Kits até 5kWp: 1 palete
- Kits 5-10kWp: 2 paletes
- Kits >10kWp: Múltiplos paletes

#### Proteção

- Embalagem específica para painéis
- Inversores em caixas originais
- Estruturas em feixe protegido
- Cabos em bobinas

### Distribuição

#### Própria

- Grandes centros urbanos
- Entrega programada
- Equipe especializada

#### Terceirizada

- Interior/regiões remotas
- Transportadoras homologadas
- Seguro total da carga

## Monitoramento e Otimização

### KPIs de Kits

#### Vendas

- **Volume**: Unidades vendidas/mês
- **Mix**: Distribuição por potência
- **Margem**: Rentabilidade por kit
- **Conversão**: Taxa de fechamento

#### Qualidade

- **Retorno**: Taxa de devolução
- **Defeitos**: Problemas reportados
- **Satisfação**: NPS dos clientes
- **Performance**: Geração vs esperado

### Otimização Contínua

#### Mensal

- Análise de vendas
- Ajuste de preços
- Revisão de estoque
- Feedback dos instaladores

#### Trimestral

- Atualização de componentes
- Novos kits
- Descontinuação de modelos
- Treinamento de equipes

## Tendências Futuras

### 2024-2025

- **Kits inteligentes**: IoT integrado
- **Flexibilidade**: Componentes modulares
- **Sustentabilidade**: Materiais recicláveis
- **Digitalização**: AR para instalação

### Tecnologias Emergentes

- **Perovskite**: Painéis ultra-eficientes
- **V2G**: Integração com veículos
- **AI**: Otimização automática
- **Blockchain**: Certificação de origem

## Atualizações e Versioning

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para informações sobre desenvolvimento de novos kits, entre em contato com o departamento de produtos YSH Solar.*