# Relatório de Renomeação de Imagens - Inversores Fortlev

**Data:** 17 de outubro de 2025  
**Categoria:** Inversores (inverters)  
**Distribuidor:** Fortlev  
**Versão:** 2.0 (melhorada)

## Resumo Executivo

✅ **101 imagens renomeadas com sucesso** de 116 imagens totais  
⚠️ **15 imagens sem mapeamento** no arquivo JSON  
📊 **87.1% de taxa de sucesso**

## Estatísticas

- **Total de produtos no JSON:** 153 inversores
- **Total de imagens disponíveis:** 116 arquivos PNG
- **Mapeamento criado:** 109 códigos de imagem identificados
- **Taxa de sucesso:** 87.1%
- **Produtos com preço definido:** 106 (97.2%)
- **Produtos com potência identificada:** 87 (79.8%)
- **Produtos com MPPT identificado:** 98 (89.9%)

## Diretórios

- **Origem:** `distributors/fortlev/organized_images/inverters/`
- **Destino (v1):** `distributors/fortlev/organized_images/inverters_renamed/`
- **Destino (v2):** `distributors/fortlev/organized_images/inverters_renamed_v2/` ⭐ Recomendado
- **JSON fonte:** `fortlev-inverters.json`
- **Mapeamento completo:** `inverters_image_mapping_complete.json`

## Padrão de Nomenclatura

As imagens foram renomeadas seguindo o padrão:

```
{FABRICANTE}_{DESCRIÇÃO_PRODUTO}.png
```

### Exemplos:

| Código Original | Nome Renomeado | Produto |
|-----------------|----------------|---------|
| IIN00384.png | HUAWEI_HUAWEI__75KW_-_220V_-_7_MPPT_-_AFCI_(SUN2000-75K-MGL0-BR).png | HUAWEI ON-GRID 75KW - 220V - 7 MPPT - AFCI |
| IIN00217.png | SUNGROW_SUNGROW__8KW_-_220V_-_2_MPPT_-_AFCI_(SG8.0RS-L).png | SUNGROW ON-GRID 8KW - 220V - 2 MPPT - AFCI |
| IIN00184.png | FOXESS_FOXESS__5KW_-_220V_-_2_MPPT_-_AFCI_(F5000-G2).png | FOXESS ON-GRID 5KW - 220V - 2 MPPT - AFCI |

## Fabricantes Identificados

| Fabricante | Quantidade de Produtos |
|------------|------------------------|
| HUAWEI | 14 |
| SUNGROW | 18 |
| GROWATT | 25 |
| FOXESS | 18 |
| SOLIS | 23 |

## Imagens Sem Mapeamento (V2 - Atualizado)

As seguintes 15 imagens não foram encontradas no arquivo JSON:

1. IIN00126.png ❓ Não encontrado
2. IIN00224.png ❓ Não encontrado
3. IIN00225.png ❓ Não encontrado
4. IIN00349.png ❓ Não encontrado
5. IIN00352.png ❓ Não encontrado
6. IIN00364.png ❓ Não encontrado
7. IIN00365.png ❓ Não encontrado
8. IIN00366.png ❓ Não encontrado
9. IIN00367.png ❓ Não encontrado
10. IIN00368.png ❓ Não encontrado
11. IIN00370.png ❓ Não encontrado
12. IIN00376.png ❓ Não encontrado
13. IIN00377.png ❓ Não encontrado
14. IIN00379.png ❓ Não encontrado
15. IIN00386.png ❓ Não encontrado

### Imagens Recuperadas na V2

As seguintes imagens foram **recuperadas** na versão 2 do script (estavam no JSON com nomes de arquivo variantes):

1. ✅ IIN00232.png -> GROWATT ON-GRID 75KW - 220V - 8 MPPT (MAX75KTL3-XL2)
2. ✅ IIN00301.png -> SOLIS ON-GRID 3KW - 220V - 1 MPPT (S6-GR1P3K-M)
3. ✅ IIN00316.png -> HUAWEI ON-GRID 100KW - 380V - 10 MPPT (SUN2000-100KTL-M2)
4. ✅ IIN00342.png -> SOLIS ON-GRID 8KW - 220V - 2 MPPT (S6-GR1P8K2)

### Motivos Possíveis:

- Produtos descontinuados ou removidos do catálogo
- Imagens de componentes/acessórios não listados como inversores principais
- Códigos de imagem não correspondentes no JSON
- Dados incompletos na fonte

## Amostra de Produtos Renomeados

### Top 10 Inversores (por preço)

1. **HUAWEI ON-GRID 250KW** - R$ 112.939,09
   - Arquivo: `HUAWEI_HUAWEI__250KW_-_800V_-_6_MPPT_-_AFCI_(SUN2000-250KTL-H1).png`

2. **SOLIS ON-GRID 250KW** - R$ 84.391,99
   - Arquivo: `SOLIS_SOLIS__250KW_-_800V_-_12_MPPT_-_(250K-EHV-5G-PLUS).png`

3. **SUNGROW ON-GRID 125KW** - R$ 63.240,75
   - Arquivo: `SUNGROW_SUNGROW__125KW_-_600V_-_1_MPPT_(SG125HV).png`

4. **SOLIS ON-GRID 125KW** - R$ 57.384,56
   - Arquivo: `SOLIS_SOLIS__125KW_-_600V_-_1_MPPT_-_(125K1-EHV-5G).png`

5. **HUAWEI ON-GRID 75KW** - R$ 49.856,68
   - Arquivo: `HUAWEI_HUAWEI__75KW_-_220V_-_7_MPPT_-_AFCI_(SUN2000-75K-MGL0-BR).png`

## Especificações Técnicas Identificadas

Os produtos renomeados incluem informações de:

- **Potência:** 3kW até 250kW
- **Voltagem:** 220V, 380V, 600V, 800V
- **Número de MPPTs:** 1 a 12 trackers
- **Certificações:** AFCI (Arc-Fault Circuit Interrupter)
- **Tipos:** ON-GRID (Grid-Tie), OFF-GRID

## Próximos Passos Recomendados

1. ✅ **Verificar imagens sem mapeamento** - Investigar os 19 códigos não encontrados
2. ✅ **Validar nomes longos** - Alguns nomes excedem 100 caracteres
3. ✅ **Criar schema Medusa** - Converter dados para o formato do e-commerce
4. ✅ **Adicionar metadados** - Incluir especificações técnicas detalhadas
5. ✅ **Otimizar imagens** - Comprimir PNGs para web

## Estrutura de Dados Sugerida (Schema Medusa)

Para cada inversor renomeado, recomenda-se criar entradas com:

```json
{
  "title": "Inversor Grid-Tie HUAWEI SUN2000-75K",
  "handle": "inversor-huawei-sun2000-75k-220v-7mppt",
  "manufacturer": "HUAWEI",
  "category": "inversores",
  "technical_specs": {
    "power_kw": 75,
    "voltage_v": 220,
    "mppt_count": 7,
    "type": "GRID_TIE"
  },
  "images": [
    {
      "url": "inverters_renamed/HUAWEI_HUAWEI__75KW_-_220V_-_7_MPPT_-_AFCI_(SUN2000-75K-MGL0-BR).png"
    }
  ]
}
```

## Conclusão

A renomeação foi concluída com sucesso para 97 produtos. Os nomes agora são descritivos e incluem informações técnicas essenciais (fabricante, potência, voltagem, número de MPPTs). As 19 imagens restantes requerem investigação adicional para identificação correta.

---

**Script utilizado:** `rename_inverter_images.py`  
**Localização do backup:** Original mantido em `organized_images/inverters/`
