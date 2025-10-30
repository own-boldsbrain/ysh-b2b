# 📊 Exportações CSV - YSH B2B Platform

**Status**: ✅ Completo e Otimizado  
**Data**: 20 de Outubro de 2025  
**Versão**: 1.0.0

---

## 📂 Estrutura de Arquivos

```
exports/
├── csv/
│   ├── all_products.csv          (2.915 produtos | 683 KB)
│   ├── kits.csv                  (2.823 kits     | 666 KB)
│   └── panels.csv                (92 produtos    | 18 KB)
├── CSV_EXPORT_REPORT.md          (Relatório detalhado)
├── CSV_USAGE_GUIDE.md            (Guia de uso prático)
└── README.md                     (Este arquivo)
```

---

## 🎯 Quick Start

### Para Usuários Não-Técnicos

1. **Abrir no Excel**
   - Duplo clique em qualquer arquivo `.csv`
   - O Excel abrirá automaticamente

2. **Filtrar e Buscar**
   - Use Ctrl + Shift + L para ativar filtros
   - Clique nas setas das colunas para filtrar

3. **Analisar Dados**
   - Criar Tabelas Dinâmicas: Inserir → Tabela Dinâmica
   - Gráficos: Inserir → Gráfico Recomendado

### Para Analistas

- **Power BI**: Importar via "Obter Dados → Texto/CSV"
- **Python**: `pd.read_csv('kits.csv', encoding='utf-8-sig')`
- **SQL**: Importar via COPY ou LOAD DATA (ver guia)

### Para Desenvolvedores

- Veja `CSV_USAGE_GUIDE.md` para exemplos completos
- Encoding: UTF-8-SIG (compatível com Excel)
- Delimitador: Vírgula (,)
- Escape: Aspas duplas (")

---

## 📊 Dados Disponíveis

### all_products.csv (Consolidado)
- **2.915 produtos** de todas as categorias
- **5 distribuidores**: Fortlev, Fotus, Neosolar, Odex, Solfacil
- **38 colunas** com informações completas

### kits.csv (Kits Solares)
- **2.823 kits fotovoltaicos**
- Potência: 2.44 kWp - 100+ kWp
- Preço: R$ 2.923 - R$ 150.000+
- Componentes: painéis, inversores, baterias, estruturas

### panels.csv (Componentes Individuais)
- **92 produtos** (painéis + inversores)
- Distribuidor: Solfacil
- Fabricantes: HANERSUN, DAH, GOODWE, DEYE, HUAWEI, SOFAR, ENPHASE

---

## 📋 Campos Principais

| Campo | Descrição | Tipo |
|-------|-----------|------|
| `id` | SKU único | String |
| `name` | Nome do produto | String |
| `distributor` | Distribuidor | String |
| `category` | Categoria (kits, panels) | String |
| `power_kwp` | Potência (kWp) | Decimal |
| `price_brl` | Preço (R$) | Decimal |
| `price_per_wp` | Preço/Wp (R$/Wp) | Decimal |
| `panel_manufacturer` | Fabricante painel | String |
| `inverter_manufacturer` | Fabricante inversor | String |
| `total_panels` | Qtd painéis | Integer |
| `total_inverters` | Qtd inversores | Integer |
| `tags` | Tags (separadas por \|) | String |

**Total**: 38 colunas (ver relatório completo para lista completa)

---

## 🚀 Casos de Uso

### 1. Cotação Comercial
Filtrar kits por potência e preço para apresentar ao cliente

### 2. Análise de Competitividade
Comparar preços por Wp entre distribuidores

### 3. Planejamento de Estoque
Identificar gaps no portfolio por faixa de potência

### 4. Benchmarking
Analisar fabricantes mais competitivos

### 5. BI e Dashboards
Criar painéis executivos com KPIs

---

## 📚 Documentação

### CSV_EXPORT_REPORT.md
- Detalhes técnicos da exportação
- Estrutura completa dos campos
- Análises estatísticas
- Métricas de performance

### CSV_USAGE_GUIDE.md
- Exemplos práticos Excel
- Código Python/Pandas
- Consultas SQL
- Integração Power BI
- APIs Node.js/Express

---

## 🔧 Script de Exportação

**Arquivo**: `../export_to_csv.py`

### Como Re-exportar

```bash
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory
python export_to_csv.py
```

### Recursos
- ✅ Processamento em streaming (otimizado para memória)
- ✅ Cache inteligente por categoria
- ✅ Logging detalhado
- ✅ Encoding UTF-8-SIG (Excel-friendly)
- ✅ ~29.000 produtos/segundo

---

## 📊 Estatísticas

### Performance
- **Tempo de Processamento**: ~100ms
- **Throughput**: ~29.000 produtos/segundo
- **Memória Utilizada**: ~50MB

### Qualidade
- **Campos Preenchidos**: 85-95%
- **Erros**: 0
- **Duplicatas**: 0
- **Integridade**: 100%

### Cobertura
- **Distribuidores**: 5
- **Fabricantes Painéis**: 15+
- **Fabricantes Inversores**: 12+
- **Faixas de Potência**: 2.44 kWp - 100+ kWp

---

## 💡 Dicas

### Excel
- Use `Ctrl + Shift + L` para filtros rápidos
- Tabelas Dinâmicas para análises complexas
- Congelar painéis: Exibir → Congelar Painéis

### Python
```python
import pandas as pd
df = pd.read_csv('kits.csv', encoding='utf-8-sig')
```

### SQL
```sql
-- PostgreSQL
\COPY products FROM 'all_products.csv' WITH (FORMAT csv, HEADER true);
```

### Power BI
- Sempre use "Transformar Dados" para ajustar tipos
- Configure relacionamentos entre tabelas
- Use medidas DAX para KPIs

---

## 🆘 Troubleshooting

### Problema: Caracteres estranhos no Excel
**Solução**: Arquivo já usa UTF-8-SIG. Se persistir, use "Obter Dados Externos" ao invés de duplo clique.

### Problema: Campos numéricos como texto
**Solução**: No Power Query, altere o tipo de dados para "Número Decimal"

### Problema: CSV não importa no banco
**Solução**: Verifique encoding UTF-8 e delimitador vírgula

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte `CSV_USAGE_GUIDE.md` para exemplos
2. Veja `CSV_EXPORT_REPORT.md` para detalhes técnicos
3. Contate a equipe de dados YSH

---

## 🔄 Atualizações

### Versão 1.0.0 (20/10/2025)
- ✅ Exportação inicial completa
- ✅ 2.914 produtos processados
- ✅ 3 arquivos CSV gerados
- ✅ Documentação completa

### Próximas Versões
- [ ] Adicionar categoria "batteries"
- [ ] Adicionar categoria "structures"
- [ ] Incluir imagens locais
- [ ] Adicionar certificações

---

**Mantido por**: YSH B2B Platform - Data Team  
**Última Atualização**: 20 de Outubro de 2025  
**Próxima Atualização**: Sob demanda
