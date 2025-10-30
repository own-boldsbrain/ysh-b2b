# MCP Hugging Face ANEEL Server

Servidor MCP (Model Context Protocol) para acesso aos datasets ANEEL hospedados no Hugging Face.

## 📋 Descrição

Este servidor MCP fornece uma interface padronizada para consultar datasets da ANEEL (Agência Nacional de Energia Elétrica) armazenados no repositório `fernando-bold/aneel-datasets` no Hugging Face.

### Features

- 🔍 **Listagem de Datasets**: Visualize todos os arquivos CSV disponíveis
- 📊 **Consultas Genéricas**: Query qualquer dataset com filtros customizados
- ⚡ **Consultas de Tarifas**: API especializada para dados de tarifas de energia
- 🚀 **Integração Project Helios**: Dados otimizados para cálculos HaaS

## 🛠️ Instalação

```bash
cd mcp-servers/huggingface-aneel
npm install
```

## 🔑 Configuração

Configure seu token do Hugging Face:

```bash
# PowerShell
$env:HF_TOKEN = "seu_token_aqui"

# Bash
export HF_TOKEN="seu_token_aqui"
```

Para obter seu token:

1. Acesse https://huggingface.co/settings/tokens
2. Crie um token com permissão de leitura

## 🚀 Uso

### Desenvolvimento

```bash
npm run dev
```

### Produção

```bash
npm run build
npm start
```

### Inspeção (Debug)

```bash
npm run inspect
```

## 🧰 Ferramentas Disponíveis

### 1. `list_aneel_datasets`

Lista todos os datasets ANEEL disponíveis.

**Parâmetros:**
- `filter` (opcional): Filtro para buscar datasets específicos

**Exemplo:**
```typescript
{
  "filter": "tarifa"
}
```

**Resposta:**
```json
{
  "total": 15,
  "datasets": [
    {
      "name": "tarifas_energia.csv",
      "size": 2048576,
      "path": "tarifas_energia.csv"
    }
  ]
}
```

### 2. `query_aneel_dataset`

Consulta um dataset específico com filtros customizados.

**Parâmetros:**
- `filename` (obrigatório): Nome do arquivo CSV
- `filters` (opcional): Objeto com filtros por coluna
- `limit` (opcional): Número máximo de resultados (padrão: 100)

**Exemplo:**
```typescript
{
  "filename": "tarifas_energia.csv",
  "filters": {
    "estado": "SP",
    "concessionaria": "CPFL"
  },
  "limit": 50
}
```

**Resposta:**
```json
{
  "filename": "tarifas_energia.csv",
  "filters": { "estado": "SP", "concessionaria": "CPFL" },
  "count": 12,
  "data": [
    {
      "concessionaria": "CPFL Paulista",
      "estado": "SP",
      "tarifa_kwh": "0.89234",
      "modalidade": "Convencional"
    }
  ]
}
```

### 3. `get_tariff_data`

Consulta especializada para dados de tarifas de energia.

**Parâmetros:**
- `concessionaria` (opcional): Nome da concessionária
- `estado` (opcional): Sigla do estado (SP, MG, RJ, etc.)
- `modalidade` (opcional): Modalidade tarifária (Convencional, Branca)
- `classe` (opcional): Classe de consumo (Residencial, Comercial, Industrial)

**Exemplo:**
```typescript
{
  "concessionaria": "CEMIG",
  "estado": "MG",
  "classe": "Residencial"
}
```

**Resposta:**
```json
{
  "query": {
    "concessionaria": "CEMIG",
    "estado": "MG",
    "classe": "Residencial"
  },
  "count": 8,
  "tarifas": [
    {
      "concessionaria": "CEMIG Distribuição",
      "estado": "MG",
      "classe": "Residencial",
      "tarifa_kwh": "0.78456",
      "modalidade": "Convencional"
    }
  ]
}
```

## 🔗 Integração com Medusa Backend

### Configuração do MCP Client

```typescript
// src/modules/tarifa-aneel/mcp-client.ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "node",
  args: ["mcp-servers/huggingface-aneel/dist/index.js"],
  env: {
    HF_TOKEN: process.env.HF_TOKEN,
  },
});

const mcpClient = new Client(
  {
    name: "medusa-backend",
    version: "1.0.0",
  },
  {
    capabilities: {},
  }
);

await mcpClient.connect(transport);
```

### Exemplo de Uso no Service

```typescript
// src/modules/tarifa-aneel/service.ts
import { mcpClient } from "./mcp-client";

async function getTarifasByConcessionaria(concessionaria: string) {
  const result = await mcpClient.callTool({
    name: "get_tariff_data",
    arguments: { concessionaria },
  });

  return JSON.parse(result.content[0].text);
}
```

## 📊 Datasets Disponíveis

Os seguintes datasets estão disponíveis no repositório `fernando-bold/aneel-datasets`:

- **tarifas_energia.csv**: Tarifas de energia por concessionária e modalidade
- **concessionarias.csv**: Cadastro de concessionárias de energia
- **geracao_distribuida.csv**: Dados de geração distribuída (GD)
- **bandeiras_tarifarias.csv**: Histórico de bandeiras tarifárias
- E mais 206 arquivos CSV...

Total: **210 arquivos, 73.2 GB**

## 🏗️ Arquitetura

```
mcp-servers/huggingface-aneel/
├── src/
│   └── index.ts          # Servidor MCP principal
├── dist/                 # Código compilado
├── package.json          # Dependências
├── tsconfig.json         # Config TypeScript
└── README.md            # Esta documentação
```

### Dependências Principais

- `@modelcontextprotocol/sdk`: ^0.5.0 - SDK do protocolo MCP
- `@huggingface/hub`: ^0.15.0 - Cliente oficial Hugging Face
- `csv-parse`: ^5.5.6 - Parser de CSV otimizado
- `zod`: ^3.23.0 - Validação de schemas

## 🔐 Segurança

- ✅ Token HF via variável de ambiente (não hardcoded)
- ✅ Validação de schemas com Zod
- ✅ Rate limiting implícito do Hugging Face Hub
- ✅ Sem armazenamento local de credenciais

## 🚦 Status do Projeto

- ✅ **Servidor MCP implementado**
- ✅ **3 ferramentas disponíveis**
- ✅ **Integração com Hugging Face Hub**
- ⏳ Integração com Medusa Backend (pendente)
- ⏳ Testes de integração (pendente)

## 🤝 Integração com Project Helios

Este servidor MCP é parte da infraestrutura **HaaS (Homologação como Serviço)** do Project Helios. Ele fornece acesso aos dados ANEEL necessários para:

1. **Cálculo de Economia Solar**: Tarifas atualizadas por região
2. **Validação de Projetos**: Dados de concessionárias e regulamentações
3. **Analytics**: Histórico de bandeiras e custos energéticos
4. **Conformidade**: Dados oficiais da ANEEL para homologação

## 📝 Licença

Propriedade de YSH B2B - Todos os direitos reservados.

---

**Desenvolvido para Project Helios - HaaS (Homologação como Serviço)**
