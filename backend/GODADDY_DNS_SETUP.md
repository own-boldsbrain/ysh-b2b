# 📋 Guia de Configuração DNS - GoDaddy

## Domínio: yellosolar.com.br

**Objetivo:** Configurar `images.yellosolar.com.br` para servir imagens via CloudFront + S3

---

## 🔐 Passo 1: Validação do Certificado SSL (ACM)

### Acesse o painel DNS do GoDaddy

1. Faça login em https://dcc.godaddy.com
2. Navegue até **Meus Produtos** → **DNS**
3. Selecione o domínio `yellosolar.com.br`

### Adicione o registro CNAME de validação

**Registro 1:**

```
Tipo:  CNAME
Nome:  _203e56279c786422abadddbc9e7f8408
Valor: _1c23df7a7bae169c229ed17fca5c22c7.xlfgrmvvlj.acm-validations.aws.
TTL:   1 hora (3600)
```

> ⚠️ **IMPORTANTE:**
> 
> - Remova `.images.yellosolar.com.br.` do final do "Nome" se o GoDaddy adicionar automaticamente
> - O GoDaddy pode solicitar apenas `_203e56279c786422abadddbc9e7f8408`
> - Certifique-se de que o "Valor" termina com ponto (`.`)

### Aguarde a validação

- ⏱️ Tempo esperado: 5-30 minutos
- ✅ Verificar status: `node scripts/check-certificate-status.js`

---

## ☁️ Passo 2: Configuração do CloudFront (após validação)

### Execute a criação da distribution

```powershell
node scripts/create-cloudfront-distribution.js
```

Este comando irá:

1. ✅ Verificar se o certificado está validado
2. ☁️ Criar CloudFront distribution
3. 🔗 Configurar origin S3 (`ysh-b2b-products`)
4. 🔐 Associar certificado SSL
5. 📋 Gerar informações DNS

---

## 🌐 Passo 3: Configuração DNS Final

### Adicione o registro CNAME para CloudFront

**Após a distribution ser criada, você receberá o domínio CloudFront:**

```tsx
Tipo:  CNAME
Nome:  images
Valor: d1234567890abc.cloudfront.net (exemplo - usar o valor real)
TTL:   1 hora (3600)
```

> 📝 **O valor real será fornecido pelo script `create-cloudfront-distribution.js`**

### Verificar propagação DNS

```powershell
nslookup images.yellosolar.com.br
```

---

## ✅ Passo 4: Testes

### 1. Verificar status da distribution
```powershell
node scripts/check-cloudfront-status.js
```

### 2. Testar acesso via CloudFront (após DNS propagar)
```powershell
Invoke-WebRequest -Uri "https://images.yellosolar.com.br/products/inversores/286844.png" -Method Head
```

### 3. URLs de exemplo
- DEYE Inversor: `https://images.yellosolar.com.br/products/inversores/286844.png`
- DEYE Inversor: `https://images.yellosolar.com.br/products/inversores/222132.png`
- DEYE Inversor: `https://images.yellosolar.com.br/products/inversores/222133.png`

---

## 📊 Resumo de Registros DNS

| Tipo  | Nome                                    | Valor                                              | Finalidade                |
|-------|----------------------------------------|----------------------------------------------------|---------------------------|
| CNAME | `_203e56279c786422abadddbc9e7f8408`    | `_1c23df7a7bae169c229ed17fca5c22c7.xlfgrmvvlj...` | Validação SSL/TLS (ACM)   |
| CNAME | `images`                               | `d1234567890abc.cloudfront.net` (exemplo)          | CloudFront Distribution   |

---

## 🔧 Scripts de Automação

| Script | Descrição |
|--------|-----------|
| `request-acm-certificate.js` | Solicita certificado SSL no ACM |
| `check-certificate-status.js` | Verifica status de validação |
| `create-cloudfront-distribution.js` | Cria distribution CloudFront |
| `check-cloudfront-status.js` | Verifica deployment da distribution |

---

## 🆘 Troubleshooting

### Certificado não validando
- ✅ Verifique se o registro CNAME foi adicionado corretamente
- ⏱️ Aguarde até 30 minutos
- 🔍 Execute: `nslookup _203e56279c786422abadddbc9e7f8408.images.yellosolar.com.br`

### CloudFront retorna erro 403
- ✅ Verifique se o bucket S3 tem política pública configurada
- ✅ Execute: `node scripts/configure-s3-public-access.js`

### DNS não propaga
- ⏱️ Aguarde até 48 horas (geralmente 5-30 minutos)
- 🔍 Teste com: `nslookup images.yellosolar.com.br 8.8.8.8`

---

## 📞 Próximos Passos

1. ✅ Adicionar registro CNAME de validação no GoDaddy
2. ⏳ Aguardar validação (5-30 min)
3. ☁️ Executar `create-cloudfront-distribution.js`
4. ⏳ Aguardar deployment (15-30 min)
5. 🌐 Adicionar registro CNAME do CloudFront no GoDaddy
6. ⏳ Aguardar propagação DNS (5-30 min)
7. 🎉 Testar acesso: `https://images.yellosolar.com.br/products/...`

---

**Certificate ARN:** `arn:aws:acm:us-east-1:773235999227:certificate/b6b7f5fc-2040-47be-9a3c-b6934d9dceaa`

**Bucket S3:** `ysh-b2b-products`

**Região:** `us-east-1`

---

*Última atualização: 21 de outubro de 2025*
