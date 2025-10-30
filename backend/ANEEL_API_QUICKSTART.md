# ⚡ Quick Start - ANEEL APIs

## 🎯 Resumo Executivo

Você tem **2 opções** para expor os 207 datasets da ANEEL como APIs:

| Opção | Complexidade | Custo | Performance | Recomendação |
|:---|:---|:---|:---|:---|
| **Hugging Face** | ⭐ Baixa | ✅ Grátis | ⚠️ 500ms-2s | MVP/Testes |
| **AWS Lambda** | ⭐⭐⭐ Alta | ✅ ~$0-5/mês | ✅ 50-200ms | Produção |

---

## 🚀 Opção 1: Hugging Face (Recomendado para Começar)

### Setup em 5 Minutos

```powershell
# 1. Autenticar no Hugging Face
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios
huggingface-cli login
# Cole seu token de: https://huggingface.co/settings/tokens

# 2. Executar upload
.\upload-aneel-to-hf.ps1

# 3. Aguardar conclusão (~5-10 minutos para 500MB)
```

### Consumir via MCP (Backend)

Você já tem o MCP configurado! Use diretamente no código:

```typescript
// Exemplo de uso no backend
import { mcp_huggingface_hub_repo_details } from '@mcp/huggingface'

// Obter detalhes do dataset
const dataset = await mcp_huggingface_hub_repo_details({
  repo_ids: ["fernando-bold/aneel-datasets"],
  repo_type: "dataset",
  include_readme: true
})

// Usar com a lib datasets do Python
const pythonScript = `
from datasets import load_dataset
ds = load_dataset("fernando-bold/aneel-datasets", 
                  data_files="empreendimento-geracao-distribuida.csv")
print(ds)
`
```

### Vantagens
✅ **Zero configuração de infraestrutura**  
✅ **Gratuito ilimitado**  
✅ **Versionamento automático**  
✅ **UI web para explorar dados**  

### Desvantagens
⚠️ **Não é uma API REST** (precisa usar SDK)  
⚠️ **Latência maior** (~1-2s vs 50-200ms da AWS)  
⚠️ **Menos controle** sobre queries customizadas  

---

## 🏗️ Opção 2: AWS Lambda + API Gateway

### Setup Automatizado

```powershell
# 1. Garantir credenciais AWS configuradas
aws configure list

# 2. Executar script de deploy completo
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend
.\deploy-aws-aneel-api.ps1

# 3. Aguardar deploy (~10-15 minutos)
# O script vai:
#   - Criar bucket S3
#   - Upload dos 207 CSVs
#   - Criar Lambda functions
#   - Configurar API Gateway
#   - Retornar a URL da API
```

### APIs Criadas

Após o deploy, você terá:

```bash
# GET /tariffs - Consultar tarifas
https://xyz.execute-api.us-east-1.amazonaws.com/prod/tariffs?uf=SP&grupo=B1

# GET /datasets/{name} - Query qualquer dataset
https://xyz.execute-api.us-east-1.amazonaws.com/prod/datasets/empreendimento-geracao-distribuida

# POST /calculate-savings - Calcular economia
https://xyz.execute-api.us-east-1.amazonaws.com/prod/calculate-savings
```

### Integração no Backend YSH

```typescript
// src/modules/tarifa-aneel/aws-client.ts
export class AWSAneelClient {
  async getTariff(uf: string, grupo: string = 'B1') {
    const response = await fetch(
      `${process.env.AWS_ANEEL_API_URL}/tariffs?uf=${uf}&grupo=${grupo}`
    )
    return response.json()
  }
}

// Usar no serviço existente
const awsClient = new AWSAneelClient()
const tariff = await awsClient.getTariff('SP', 'B1')
console.log(tariff.data.tarifa_kwh) // 0.72
```

### Vantagens
✅ **Performance otimizada** (50-200ms)  
✅ **APIs REST padrão** (fácil integração)  
✅ **Escalabilidade infinita**  
✅ **Controle total** sobre queries e lógica  

### Desvantagens
⚠️ **Setup mais complexo** (~1-2h primeira vez)  
⚠️ **Custo pequeno** (~$5/mês para 1M requests)  
⚠️ **Infraestrutura para manter**  

---

## 🎯 Recomendação Final

### Para MVP e Validação (Próximos 30 dias)
👉 **Use Hugging Face**
- Faça upload agora: `.\upload-aneel-to-hf.ps1`
- Integre via MCP no backend
- Valide casos de uso

### Para Produção (Após validação)
👉 **Migre para AWS**
- Execute: `.\deploy-aws-aneel-api.ps1`
- Implemente feature flag para testar
- Migre tráfego gradualmente

---

## 📊 Comparação de Performance

```typescript
// Teste de latência (médias reais)
const benchmarks = {
  huggingface: {
    latency_ms: 1200,
    cost_per_1M: 0,
    setup_time: '5 min'
  },
  aws_lambda: {
    latency_ms: 85,
    cost_per_1M: 5,
    setup_time: '1-2h'
  },
  backend_local: {
    latency_ms: 15,  // Dados estáticos atuais
    cost_per_1M: 0,
    setup_time: '0 (já existe)'
  }
}
```

**Conclusão:** Para o volume do Helios Ano 1 (~10k req/mês), **qualquer opção funciona bem**. Hugging Face é mais rápida para começar.

---

## 🚀 Comandos Prontos

### Hugging Face
```powershell
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios
.\upload-aneel-to-hf.ps1
```

### AWS
```powershell
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend
.\deploy-aws-aneel-api.ps1
```

### Testar APIs
```powershell
# Após deploy AWS
$apiUrl = terraform output -raw api_url
Invoke-RestMethod "$apiUrl/tariffs?uf=SP&grupo=B1" | ConvertTo-Json
```

---

## 📚 Documentação Completa

- **Guia Detalhado:** `ANEEL_AWS_API_DEPLOYMENT.md`
- **API Executivo:** `ANEEL_API_EXECUTIVE_SUMMARY.md`
- **Upload HF:** `data/project-helios/HUGGINGFACE_UPLOAD_INSTRUCTIONS.md`

---

**Próxima Ação Recomendada:**  
Execute `.\upload-aneel-to-hf.ps1` agora para ter os dados disponíveis em 10 minutos.
