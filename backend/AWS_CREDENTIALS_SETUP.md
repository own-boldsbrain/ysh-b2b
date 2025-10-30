# 🔐 AWS CREDENTIALS SETUP GUIDE

## Status Atual

```
AWS CLI:      ✅ Instalado (v2.31.18)
Credenciais:  ❌ Não configuradas
Próximo:      ⏳ Configurar credenciais
```

---

## 📋 OBTER CREDENCIAIS AWS

### Passo 1: Acessar AWS Console

1. Abra: **https://console.aws.amazon.com**
2. Faça login com sua conta AWS

### Passo 2: Navegar para IAM

```
Console → IAM (Identity & Access Management)
  ↓
Users
  ↓
[Seu Nome de Usuário]
  ↓
Security Credentials
```

### Passo 3: Criar Access Key

1. Clique em **"Create access key"**
2. Selecione **"Command Line Interface (CLI)"**
3. Marque a confirmação
4. Clique **"Next"**
5. Opcional: adicione descrição (ex: "YSH B2B AWS Deployment")
6. Clique **"Create access key"**

### Passo 4: Copiar Credenciais

Você verá:
- **Access Key ID**: Copie este valor
- **Secret Access Key**: Copie este valor (única vez que aparece!)
- **Console sign-in URL**: Ignore por enquanto

⚠️ **IMPORTANTE**: Guarde estas credenciais em local seguro!

---

## ⚙️ CONFIGURAR AWS CLI

### Opção 1: Script Interativo (RECOMENDADO)

Execute no PowerShell:

```powershell
.\scripts\setup-aws-credentials.ps1
```

O script irá:
1. Solicitar Access Key ID
2. Solicitar Secret Access Key
3. Confirmar região (us-east-1 padrão)
4. Validar as credenciais
5. Salvar em `~/.aws/credentials`

### Opção 2: Comando Manual

Execute no PowerShell ou Cmd:

```powershell
aws configure
```

Quando solicitado, insira:

```
AWS Access Key ID [None]:       → Copie do AWS Console
AWS Secret Access Key [None]:   → Copie do AWS Console
Default region name [None]:     → us-east-1
Default output format [None]:   → json
```

---

## ✅ VALIDAR CONFIGURAÇÃO

### Teste 1: Verificar Identidade

```powershell
aws sts get-caller-identity
```

**Resultado esperado:**
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

Se funcionar, você está pronto!

### Teste 2: Listar S3 Buckets

```powershell
aws s3 ls
```

Deve listar os buckets S3 existentes (ou estar vazio se nenhum bucket).

### Teste 3: Testar com Script

```powershell
node scripts/test-connectivity.js
```

Testa:
- ✅ AWS STS
- ✅ S3
- ✅ DynamoDB
- ✅ Facebook API
- ✅ Latência de rede

---

## 📁 ONDE AS CREDENCIAIS SÃO SALVAS

### Estrutura de Arquivos

```
%USERPROFILE%\.aws\
├── credentials      ← Chaves de acesso (secreto!)
├── config          ← Configurações (região, formato)
└── credentials.backup.[timestamp]  ← Backup automático
```

### Exemplo de Conteúdo

**`~/.aws/credentials`:**
```
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**`~/.aws/config`:**
```
[default]
region = us-east-1
output = json
```

---

## 🐛 TROUBLESHOOTING

### ❌ "Unable to locate credentials"

**Causa:** Credenciais não configuradas

**Solução:**
```powershell
aws configure
# ou
.\scripts\setup-aws-credentials.ps1
```

### ❌ "InvalidSignatureException"

**Causa:** Credenciais incorretas

**Solução:**
1. Verifique se Access Key ID está correto
2. Verifique se Secret Access Key está correto
3. Se duvidoso, crie uma nova access key no AWS Console

### ❌ "AccessDenied"

**Causa:** Usuário não tem permissões suficientes

**Solução:**
1. Verifique se o usuário tem policy `AdministratorAccess` ou equivalente
2. Ou crie um usuário com permissões IAM completas

### ❌ "NoCredentialProviders"

**Causa:** Credenciais não estão sendo lidas

**Solução:**
1. Reinicie o terminal
2. Verifique se `~/.aws/credentials` existe
3. Execute `aws configure` novamente

### ❌ "The security token included in the request is invalid"

**Causa:** Access key foi revogada ou expirou

**Solução:**
1. Crie uma nova access key no AWS Console
2. Configure novamente com `aws configure`

---

## 🔒 SEGURANÇA

### Boas Práticas

✅ **Faça:**
- Guarde credenciais em local seguro
- Use diferentes access keys para diferentes ambientes
- Revogue access keys antigas
- Use MFA quando possível

❌ **Não Faça:**
- Compartilhe credenciais
- Commita `.aws/credentials` no Git
- Exponha credenciais em logs
- Use credenciais root da conta

### Arquivo `.gitignore`

Certifique-se de que `.aws/` está no `.gitignore`:

```
.aws/
.env
.env.local
secrets/
```

---

## 📋 PRÓXIMOS PASSOS

### Após Validar Credenciais

1. **Validar conectividade completa:**
   ```powershell
   node scripts/test-connectivity.js
   ```

2. **Verificar setup pré-deployment:**
   ```powershell
   node scripts/verify-aws-setup.js
   ```

3. **Deploy CloudFormation stack:**
   ```powershell
   .\aws-cloudformation\deploy-stack.ps1
   ```

4. **Upload de dados:**
   ```powershell
   node scripts/upload-to-aws.js
   ```

5. **Sincronizar com Meta:**
   ```powershell
   node scripts/sync-facebook-from-aws.js
   ```

---

## 📞 REFERÊNCIA RÁPIDA

### Comandos AWS CLI

```powershell
# Verificar credenciais
aws sts get-caller-identity

# Listar S3 buckets
aws s3 ls

# Listar DynamoDB tables
aws dynamodb list-tables

# Listar CloudFormation stacks
aws cloudformation list-stacks

# Obter informações de stack
aws cloudformation describe-stacks --stack-name ysh-b2b-production

# Ver logs de erro
aws cloudformation describe-stack-events --stack-name ysh-b2b-production
```

---

## ⏱️ TEMPO ESTIMADO

| Tarefa | Tempo |
|--------|-------|
| Obter credenciais AWS | 2-3 min |
| Configurar AWS CLI | 2-3 min |
| Validar credenciais | 1-2 min |
| **TOTAL** | **5-8 min** |

---

## ✨ STATUS

Quando você tiver completado:
- ✅ Obter Access Key ID e Secret Access Key
- ✅ Executar `aws configure` ou script setup
- ✅ Validar com `aws sts get-caller-identity`

Você estará pronto para:
- ✅ Deploy CloudFormation stack
- ✅ Upload de imagens e SKUs
- ✅ Sincronização com Meta

---

**Última atualização:** 21 de outubro de 2025  
**Status:** Aguardando credenciais AWS
