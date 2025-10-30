# ☁️ AWS vs Alibaba Cloud - Análise Free Tier para ANEEL APIs

## 🎯 Contexto do Projeto

**Necessidades:**

- Hospedar 207 arquivos CSV (~500MB total)
- Servir APIs serverless para consulta de dados ANEEL
- ~10.000 requests/mês (Ano 1 do Helios)
- Escalabilidade para 100.000+ requests/mês (Ano 3)

---

## 🏆 Comparação Free Tier

### AWS Free Tier

| Serviço | Free Tier | Duração | Após Free Tier |
|:---|:---|:---|:---|
| **Lambda** | 1M requests/mês<br/>400.000 GB-seg compute | ✅ Permanente | $0.20 por 1M requests |
| **API Gateway** | ❌ Não tem free tier | - | $3.50 por 1M requests |
| **S3** | 5GB storage<br/>20.000 GET<br/>2.000 PUT | ⏰ 12 meses | $0.023/GB/mês<br/>$0.0004 por 1k GET |
| **CloudFront** | 1TB transfer/mês | ✅ Permanente | $0.085/GB |
| **DynamoDB** | 25GB storage<br/>25 RCU/WCU | ✅ Permanente | $1.25/milhão de WCU |

**Total Estimado para o Projeto:**

- **Ano 1 (10k req/mês):** ~$0.04/mês ⚠️ (API Gateway cobra desde o 1º request)
- **Ano 2 (50k req/mês):** ~$0.18/mês (S3 passa a cobrar após 12 meses)
- **Ano 3 (100k req/mês):** ~$0.36/mês

> ⚠️ **Correção Importante:** API Gateway não tem free tier, cobra $3.50 por milhão de requests desde o início
> 
> 💡 **Otimização:** Use Lambda Function URLs (sem API Gateway) para custo zero até exceder 1M requests/mês

---

### Alibaba Cloud Free Tier

| Serviço | Free Tier | Duração | Após Free Tier |
|:---|:---|:---|:---|
| **Function Compute** | 1M invocations/mês<br/>400.000 GB-seg | ✅ Permanente | ¥0.0000017/invocation |
| **API Gateway** | 1M requests/mês | ⏰ 6 meses | ¥0.06 por 10k requests |
| **OSS (Object Storage)** | 5GB storage<br/>5GB tráfego | ⏰ 6 meses | ¥0.12/GB/mês<br/>¥0.50/GB tráfego |
| **CDN** | 10GB tráfego | ⏰ 6 meses | ¥0.24/GB |
| **Table Store** | 25GB storage<br/>100M reads | ⏰ 6 meses | ¥1.0/GB/mês |

**Total Estimado para o Projeto:**
- **Primeiros 6 meses (10k req/mês):** $0/mês ✅ Grátis
- **Após 6 meses (10k req/mês):** ~$2-3/mês ⚠️
- **Ano 3 (100k req/mês):** ~$8-10/mês ⚠️

---

## 📊 Análise Detalhada por Critério

### 1. 💰 Custo Total de Propriedade (TCO)

```
Projeção 3 Anos - Cenário Helios Real
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AWS:
├─ Ano 1 (10k req/mês):    $0.04/mês × 12 = $0.48
├─ Ano 2 (50k req/mês):    $0.18/mês × 12 = $2.16
└─ Ano 3 (100k req/mês):   $0.36/mês × 12 = $4.32
                           TOTAL 3 ANOS: $6.96

💡 Alternativa com Lambda Function URLs (sem API Gateway):
├─ Ano 1 (10k req/mês):    $0/mês × 12 = $0
├─ Ano 2 (50k req/mês):    $0/mês × 12 = $0
└─ Ano 3 (100k req/mês):   $0/mês × 12 = $0
                           TOTAL 3 ANOS: $0 ✅

Alibaba Cloud:
├─ Meses 1-6 (10k req/mês): $0/mês × 6 = $0
├─ Meses 7-12 (10k req/mês): $2/mês × 6 = $12
├─ Ano 2 (50k req/mês):     $5/mês × 12 = $60
└─ Ano 3 (100k req/mês):    $10/mês × 12 = $120
                            TOTAL 3 ANOS: $192
```

**Vencedor: AWS** 💰 (Economia de $185 em 3 anos com API Gateway, ou $192 com Lambda URLs)

---

### 2. 🚀 Performance & Latência

#### AWS
```
Latência Típica (Brasil → us-east-1 ou sa-east-1):
├─ Lambda cold start: 800-1200ms (us-east-1) | 400-800ms (sa-east-1)
├─ Lambda warm: 50-150ms (us-east-1) | 20-80ms (sa-east-1)
├─ S3 read: 20-80ms (us-east-1) | 10-30ms (sa-east-1)
├─ API Gateway: +10-20ms
└─ CloudFront (edge): 15-50ms (cache hit)
   TOTAL: ~85-270ms warm (us-east-1) | ~45-150ms warm (sa-east-1)
          ~850-1300ms cold (us-east-1) | ~440-880ms cold (sa-east-1)

⚠️ Recomendação: Use sa-east-1 (São Paulo) para latência 50% menor
💡 Mitigue cold starts com: Provisioned Concurrency ou Lambda SnapStart
```

**Edge Locations no Brasil:**

- São Paulo (GRU)
- Rio de Janeiro (GIG)
- Fortaleza (FOR)

#### Alibaba Cloud
```
Latência Típica (Brasil → Nearest Region):
├─ Function cold start: 1000-1500ms
├─ Function warm: 80-200ms
├─ OSS read: 100-300ms (sem region BR)
├─ API Gateway: +20-40ms
└─ CDN: 50-150ms
   TOTAL: ~250-690ms (warm) | ~1200-2000ms (cold)
```

**Edge Locations no Brasil:**
- ⚠️ **Nenhuma** - Region mais próximo é US West

**Vencedor: AWS** ⚡ (~3x mais rápido)

---

### 3. 🌍 Presença no Brasil

| Aspecto | AWS | Alibaba Cloud |
|:---|:---|:---|
| **Data Centers** | São Paulo (sa-east-1) ✅ | Nenhum ❌ |
| **Edge Locations** | 3 cidades (SP, RJ, FOR) ✅ | 0 ❌ |
| **Latência Média** | 15-50ms ✅ | 200-500ms ⚠️ |
| **Compliance LGPD** | Total ✅ | Parcial ⚠️ |
| **Suporte PT-BR** | 24/7 ✅ | Limitado ⚠️ |

**Vencedor: AWS** 🇧🇷 (Presença local crítica)

---

### 4. 🛠️ Facilidade de Uso

#### AWS
```typescript
// Ecosystem Maturo
✅ Terraform provider robusto
✅ CDK para IaC em TypeScript/Python
✅ SAM para deploy simplificado
✅ Documentação extensa PT-BR
✅ Comunidade brasileira grande
✅ Integração nativa com GitHub Actions
✅ CloudFormation templates prontos
```

#### Alibaba Cloud
```typescript
// Ecosystem em Crescimento
⚠️ Terraform provider com menos features
⚠️ Documentação majoritariamente em inglês/chinês
⚠️ Comunidade brasileira pequena
⚠️ Menos exemplos/tutoriais
✅ Interface similar à AWS (migrável)
✅ CLI bem estruturada
```

**Vencedor: AWS** 🧰 (Ecosystem superior)

---

### 5. 🔐 Segurança & Compliance

| Critério | AWS | Alibaba Cloud |
|:---|:---|:---|
| **Certificações BR** | ISO 27001, PCI-DSS, SOC 1/2/3 | ISO 27001 |
| **LGPD Compliance** | ✅ Full (data in BR) | ⚠️ Parcial (data fora BR) |
| **Penetration Testing** | Permitido sem aprovação | Requer aprovação |
| **Audit Logs** | CloudTrail (granular) | ActionTrail (menos granular) |
| **IAM Granularity** | Extrema (1000+ policies) | Boa (500+ policies) |

**Vencedor: AWS** 🔒 (Compliance crítico para B2B)

---

### 6. 📈 Escalabilidade

#### Limites do Free Tier AWS
```
Lambda:
├─ Invocations: 1M/mês permanente
├─ Compute: 400k GB-seg/mês permanente
└─ Concurrent: 1000 (pode aumentar via quota)

S3:
├─ Storage: Ilimitado (paga após 5GB/12 meses)
├─ Requests: Ilimitados (paga $0.0004/1k)
└─ Transfer: Ilimitado via CloudFront (1TB/mês grátis)
```

**Cenário de Estresse (1M requests/mês):**
```typescript
const awsCost = {
  lambda: 0, // Dentro do free tier permanente (1M invocações)
  apiGateway: 3.50, // ⚠️ NÃO TEM FREE TIER - cobra sempre
  s3Storage: 0.023 * 0.5, // 500MB = $0.01 (após 12 meses)
  s3Requests: 0.0004 * 1000, // 1M GETs = $0.40
  cloudfront: 0, // Dentro do free tier permanente (1TB/mês)
  total: 3.91 // por mês - CORRIGIDO
}

// 💡 OTIMIZAÇÃO: Use Lambda Function URLs (sem API Gateway)
const awsCostOptimized = {
  lambda: 0, // Dentro do free tier permanente
  s3Storage: 0.01, // 500MB após 12 meses
  s3Requests: 0.40, // 1M GETs
  cloudfront: 0, // Free tier permanente
  total: 0.41 // por mês - 90% de economia! ✅
}
```

#### Limites do Free Tier Alibaba
```
Function Compute:
├─ Invocations: 1M/mês permanente
├─ Compute: 400k GB-seg/mês permanente
└─ Concurrent: 100 (limite baixo)

OSS:
├─ Storage: 5GB por 6 meses apenas
├─ Requests: Limitados
└─ Transfer: 5GB por 6 meses apenas
```

**Mesmo Cenário (1M requests/mês após free tier):**
```typescript
const alibabaCost = {
  functionCompute: 0, // Dentro do free tier permanente
  apiGateway: (1000 * 0.06), // 1M requests = $60 CNY ~ $8.50
  ossStorage: 0.12 * 0.5, // 500MB = $0.06
  ossRequests: 0.50 * 1, // 1M GETs ~ $0.50
  cdn: 0.24 * 10, // 10GB transfer = $2.40
  total: 11.46 // por mês
}
```

**Vencedor: AWS** 📈 (Escala com custo 3x menor - $3.91 vs $11.46 com API Gateway, ou 27x menor com Lambda URLs)

---

### 7. 🔄 Integrações & Ecosystem

#### AWS Integrations para YSH B2B
```typescript
const awsEcosystem = {
  // Já em uso no projeto
  s3: '✅ Storage de imagens de produtos',
  cloudfront: '✅ CDN para assets estáticos',
  acm: '✅ Certificados SSL',
  route53: '⚠️ DNS (pode usar GoDaddy)',
  
  // Fácil de adicionar
  cognito: 'Autenticação de usuários',
  ses: 'Envio de emails transacionais',
  sns: 'Notificações push',
  sqs: 'Filas para processamento assíncrono',
  eventbridge: 'Event-driven architecture',
  
  // Integração nativa
  github_actions: '✅ CI/CD já configurado',
  terraform: '✅ IaC maduro',
  datadog: 'Monitoring APM',
  sentry: 'Error tracking'
}
```

#### Alibaba Cloud Integrations
```typescript
const alibabaEcosystem = {
  // Equivalentes
  oss: 'Similar ao S3',
  cdn: 'Similar ao CloudFront',
  cas: 'Similar ao ACM',
  dns: 'Similar ao Route53',
  
  // Limitado
  directMail: 'Email (menos confiável que SES)',
  mns: 'Message queue (menos features que SQS)',
  
  // Integração
  github_actions: '⚠️ Menos exemplos',
  terraform: '⚠️ Provider menos maduro',
  monitoring: '⚠️ Ferramentas próprias'
}
```

**Vencedor: AWS** 🔗 (Ecosystem completo)

---

## 🎯 Recomendação Final

### ✅ **AWS é a Melhor Escolha** para o Project Helios

#### Razões Decisivas:

1. **Custo 3 Anos:** $0-7 (AWS) vs $192 (Alibaba) → **Economia de 96-100%**
2. **Performance:** 3x mais rápido devido a presença local no Brasil (use sa-east-1)
3. **Free Tier Permanente:** Lambda e CloudFront grátis para sempre
4. **LGPD Compliance:** Dados hospedados em São Paulo (sa-east-1)
5. **Ecosystem:** Já usa AWS (S3, CloudFront, ACM)
6. **Suporte:** Documentação PT-BR e comunidade local
7. **Escalabilidade:** Suporta crescimento até Série A com custo mínimo

#### 💡 Otimização Recomendada:

**Use Lambda Function URLs** em vez de API Gateway para:
- ✅ Custo zero até 1M requests/mês
- ✅ Latência 10-20ms menor
- ✅ Setup mais simples
- ⚠️ Menos features (sem rate limiting, API keys, etc)

#### Quando Considerar Alibaba Cloud?

- ❌ Projeto focado na China
- ❌ Necessidade de compliance chinês
- ❌ Parceria comercial com Alibaba
- ❌ Nenhum desses se aplica ao Helios

---

## 🚀 Plano de Ação Recomendado

### Fase 1: Deploy Imediato (Hoje)
```powershell
# 1. Upload para Hugging Face (backup/testes)
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios
.\upload-aneel-to-hf.ps1

# 2. Deploy AWS (produção)
cd ..\..\
.\deploy-aws-aneel-api.ps1
```

**Resultado:** APIs prontas em 30 minutos, custo $0/mês

### Fase 2: Integração Backend (Semana 1)
```typescript
// Adicionar client AWS no serviço ANEEL
import { AWSAneelClient } from './aws-client'

const client = new AWSAneelClient({
  baseUrl: process.env.AWS_ANEEL_API_URL
})

// Feature flag para testar gradualmente
const useAWS = process.env.ANEEL_USE_AWS === 'true'
const tariff = useAWS 
  ? await client.getTariff('SP', 'B1')
  : localFallback('SP', 'B1')
```

### Fase 3: Monitoramento (Semana 2)
```typescript
// CloudWatch Dashboards
- Lambda invocations/errors
- API Gateway latency
- S3 request counts
- CloudFront cache hit ratio
```

---

## 📊 Resumo Executivo

| Critério | AWS | Alibaba | Vencedor |
|:---|:---:|:---:|:---|
| **Custo (3 anos)** | $0-7 | $192 | 🏆 AWS |
| **Performance (latência)** | 45-150ms | 250ms | 🏆 AWS |
| **Free Tier (duração)** | Permanente | 6 meses | 🏆 AWS |
| **Presença Brasil** | ✅ SP | ❌ | 🏆 AWS |
| **LGPD Compliance** | ✅ | ⚠️ | 🏆 AWS |
| **Ecosystem** | Maduro | Crescendo | 🏆 AWS |
| **Documentação PT-BR** | ✅ | ❌ | 🏆 AWS |
| **Integração YSH** | Nativa | Nova | 🏆 AWS |

**Score Final:** AWS 8-0 Alibaba

---

## 💡 Alternativa Híbrida (Não Recomendada)

Se por algum motivo precisar usar ambas:

```typescript
// Multi-cloud strategy (complexidade desnecessária)
const providers = {
  primary: 'AWS',        // Produção Brasil
  backup: 'Alibaba',     // Disaster recovery
  dev: 'Hugging Face'    // Testes/MVP
}

// Adiciona latência, custo de manutenção e complexidade
// Não vale a pena para o volume do Helios
```

---

## 🎯 Conclusão

**Use AWS com Lambda Function URLs.** É mais barato (custo zero para o volume do Helios), mais rápido (deploy em sa-east-1), e você já está parcialmente integrado.

### 💰 Custo Real Esperado:

- **Ano 1-3 com Lambda URLs:** $0/mês (100% dentro do free tier)
- **Ano 1-3 com API Gateway:** ~$0.04-0.36/mês
- **Após crescimento (1M req/mês):** $0.41-3.91/mês vs $11.46/mês (Alibaba)

### ⚡ Checklist de Otimização:

- ✅ **Use Lambda Function URLs** (em vez de API Gateway)
- ✅ **Deploy em sa-east-1** (São Paulo) para latência mínima
- ✅ **Habilite CloudFront** com cache agressivo (TTL 1h+)
- ✅ **Comprima CSVs** no S3 (gzip pode reduzir 80% do tamanho)
- ⚠️ **Provisioned Concurrency** apenas se cold starts forem críticos (adiciona custo)

### 🚫 Por Que Não Alibaba?

Alibaba Cloud só faria sentido se:
- ❌ Tivesse operação significativa na China
- ❌ Necessitasse compliance chinês específico
- ❌ Houvesse parceria comercial com Alibaba

**Nenhum desses se aplica ao Project Helios.**

**Próxima Ação:** Execute `.\deploy-aws-aneel-api.ps1` agora.

---

**Documento:** AWS vs Alibaba Cloud Comparison  
**Versão:** 1.0  
**Data:** 21 de Outubro de 2025  
**Decisão:** ✅ AWS Free Tier
