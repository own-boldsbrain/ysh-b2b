# Painéis Solares - Padrão SKU YSH

## Visão Geral

Este documento detalha os padrões de nomenclatura (SKU) para painéis solares fotovoltaicos utilizados nos projetos YSH Solar. O padrão estabelecido garante consistência na identificação, catalogação e gerenciamento do inventário de painéis.

## Padrão SKU

### Formato
```
PNL-{MANUFACTURER}-{MODEL}-{POWER}W[-{TECH}]
```

### Componentes da SKU

1. **PNL**: Prefixo fixo identificando painéis solares
2. **MANUFACTURER**: Código de 3-5 letras do fabricante 
3. **MODEL**: Modelo específico do painel
4. **POWER**: Potência em Watts
5. **TECH**: Tecnologia opcional (MONO, POLY, PERC, BF, TOPCON, etc.)

### Exemplos
- `PNL-CANA-CS7N-550MS-550W-MONO`
- `PNL-JINKO-TIGER-NEO-550W-NTYPE`
- `PNL-LONGI-LR5-72HPH-540W-HPBC`

## Fabricantes Aprovados

### Tier 1 (Premium)
| Código | Fabricante | País | Série Principal |
|--------|------------|------|-----------------|
| CANA | Canadian Solar | Canadá | CS7N, CS6R, HiKu7 |
| JINKO | Jinko Solar | China | Tiger Neo, Tiger Pro |
| LONGI | LONGi Solar | China | Hi-MO X6, LR5-72HPH |
| TRINA | Trina Solar | China | Vertex S+, Honey M+ |

### Tier 2 (Performance)
| Código | Fabricante | País | Série Principal |
|--------|------------|------|-----------------|
| JA | JA Solar | China | JAM72S30, DeepBlue 4.0 |
| RISEN | Risen Energy | China | RSM150-8, Hyper-ion |
| PHONO | Phono Solar | China | PS-M6, Twin Peak |
| QCELLS | Q CELLS | Alemanha | Q.PEAK DUO, Q.MAXX |

### Nacionais
| Código | Fabricante | País | Série Principal |
|--------|------------|------|-----------------|
| SOLNP | Solar N Plus | Brasil | SNP-M, SNP-P |
| UPSOL | UP Solar | Brasil | UPS-M, UPS-P |

## Tecnologias

### Tipos de Células
- **MONO**: Monocristalino padrão
- **POLY**: Policristalino 
- **PERC**: Passivated Emitter Rear Cell
- **BF**: Bifacial (ambas as faces geram energia)
- **TOPCON**: Tunnel Oxide Passivated Contact
- **NTYPE**: Células tipo N de alta eficiência
- **HPBC**: Heterojunction with Passivated Back Contact

### Aplicações por Tecnologia
- **Residencial**: MONO, PERC, NTYPE
- **Comercial**: MONO, PERC, BF, TOPCON
- **Utility Scale**: BF, TOPCON, NTYPE, HPBC

## Especificações Técnicas

### Campos Obrigatórios
- `manufacturer`: Fabricante do painel
- `model`: Modelo específico
- `power_rating_w`: Potência nominal em Watts
- `cell_technology`: Tecnologia das células
- `efficiency_percent`: Eficiência do módulo
- `voltage_vmp`: Tensão no ponto de máxima potência
- `current_imp`: Corrente no ponto de máxima potência
- `dimensions_mm`: Dimensões (comprimento x largura x espessura)
- `weight_kg`: Peso em quilogramas
- `warranty_years`: Garantia em anos

### Campos Opcionais
- `voltage_voc`: Tensão de circuito aberto
- `current_isc`: Corrente de curto-circuito
- `temp_coeff_power`: Coeficiente de temperatura
- `temp_coeff_voltage`: Coeficiente de temperatura da tensão
- `temp_coeff_current`: Coeficiente de temperatura da corrente
- `fire_class`: Classe de fogo (A, B, C)
- `ip_rating`: Grau de proteção IP
- `certifications`: Certificações (IEC, UL, etc.)
- `pld_percent`: Power Limited Degradation
- `bifaciality_percent`: Bifacialidade (para painéis BF)

## Faixas de Potência

### Residencial (1-10kW)
- **Compactos**: 300-450W (espaço limitado)
- **Padrão**: 450-550W (maioria das instalações)
- **Alta Potência**: 550-650W (máxima geração)

### Comercial (10-100kW)
- **Padrão**: 450-550W (custo-benefício)
- **Alta Eficiência**: 550-650W (área limitada)
- **Bifaciais**: 550-700W (máximo aproveitamento)

### Industrial/Utility (100kW+)
- **Monofaciais**: 550-650W
- **Bifaciais**: 600-700W+
- **Trackers**: Especialmente 650W+ bifaciais

## Exemplos de Produtos

### Canadian Solar CS7N-550MS
```json
{
  "sku": "PNL-CANA-CS7N-550MS-550W-MONO",
  "manufacturer": "Canadian Solar",
  "model": "CS7N-550MS",
  "power_rating_w": 550,
  "cell_technology": "MONO_PERC",
  "efficiency_percent": 21.4,
  "voltage_vmp": 41.7,
  "current_imp": 13.19,
  "dimensions_mm": "2278x1134x35",
  "weight_kg": 28.7,
  "warranty_years": 25,
  "certifications": ["IEC61215", "IEC61730", "UL1703"],
  "price_brl": 485.00
}
```

### Jinko Tiger Neo 580W
```json
{
  "sku": "PNL-JINKO-TIGER-NEO-580W-NTYPE",
  "manufacturer": "Jinko Solar",
  "model": "Tiger Neo 580W",
  "power_rating_w": 580,
  "cell_technology": "N_TYPE_TOPCON",
  "efficiency_percent": 22.3,
  "voltage_vmp": 44.5,
  "current_imp": 13.03,
  "dimensions_mm": "2278x1134x30",
  "weight_kg": 28.9,
  "warranty_years": 25,
  "bifaciality_percent": 85,
  "price_brl": 525.00
}
```

## Validação e Controle de Qualidade

### Critérios de Aprovação
1. **Eficiência mínima**: 19% (residencial), 20% (comercial)
2. **Garantia mínima**: 20 anos produto, 25 anos performance
3. **Certificações obrigatórias**: IEC61215, IEC61730
4. **Tier ranking**: Somente Tier 1 e Tier 2 (Bloomberg NEF)

### Processo de Validação
1. Verificação de certificações
2. Teste de amostras em laboratório
3. Aprovação do comitê técnico
4. Inclusão no catálogo aprovado

## Integração com Sistemas

### Medusa.js
Todos os painéis são automaticamente sincronizados com o catálogo Medusa.js através do pipeline de dados, incluindo:
- Especificações técnicas completas
- Preços e disponibilidade
- Imagens e documentação
- Categorização automática

### Meta Commerce
Integração completa com Facebook Catalog Manager para:
- Anúncios dinâmicos
- Retargeting por categoria
- Comparação de produtos
- Otimização de conversão

## Atualizações e Versioning

Este documento segue versionamento semântico:
- **Major**: Mudanças no formato SKU
- **Minor**: Novos fabricantes ou tecnologias
- **Patch**: Correções e atualizações de especificações

**Versão Atual**: 2.0.0  
**Última Atualização**: 19 de outubro de 2024  
**Próxima Revisão**: Janeiro de 2025

---

*Para dúvidas ou sugestões sobre este padrão, entre em contato com a equipe técnica YSH Solar.*