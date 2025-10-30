# 🔑 AWS ACCOUNT SETUP - KMS Key Policy & Credentials

## 📋 Informações da Sua Conta AWS

**Account ID:** `773235999227`  
**KMS Key Policy Status:** ✅ Configurado  
**Data:** 21 de outubro de 2025

---

## 🔐 Sua Política de Chaves KMS (Key Management Service)

Sua conta AWS já possui uma **chave KMS pré-configurada** com a seguinte política:

### Política Atual (key-consolepolicy-3)

```json
{
  "Id": "key-consolepolicy-3",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::773235999227:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow access for Key Administrators",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::773235999227:role/AIOpsRole-DefaultInvestigationGroup-twa9pf",
          "arn:aws:iam::773235999227:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_c007a985b3eea5a7",
          "arn:aws:iam::773235999227:role/aws-service-role/q.amazonaws.com/AWSServiceRoleForAmazonQDeveloper",
          "arn:aws:iam::773235999227:role/aws-service-role/notifications.amazonaws.com/AWSServiceRoleForAwsUserNotifications",
          "arn:aws:iam::773235999227:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
          "arn:aws:iam::773235999227:role/aws-service-role/organizations.amazonaws.com/AWSServiceRoleForOrganizations",
          "arn:aws:iam::773235999227:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
          "arn:aws:iam::773235999227:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
        ]
      },
      "Action": [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:TagResource",
        "kms:UntagResource",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion",
        "kms:RotateKeyOnDemand"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::773235999227:role/AIOpsRole-DefaultInvestigationGroup-twa9pf",
          "arn:aws:iam::773235999227:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_c007a985b3eea5a7",
          "arn:aws:iam::773235999227:role/aws-service-role/q.amazonaws.com/AWSServiceRoleForAmazonQDeveloper",
          "arn:aws:iam::773235999227:role/aws-service-role/notifications.amazonaws.com/AWSServiceRoleForAwsUserNotifications",
          "arn:aws:iam::773235999227:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
          "arn:aws:iam::773235999227:role/aws-service-role/organizations.amazonaws.com/AWSServiceRoleForOrganizations",
          "arn:aws:iam::773235999227:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
          "arn:aws:iam::773235999227:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
        ]
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow attachment of persistent resources",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::773235999227:role/AIOpsRole-DefaultInvestigationGroup-twa9pf",
          "arn:aws:iam::773235999227:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_c007a985b3eea5a7",
          "arn:aws:iam::773235999227:role/aws-service-role/q.amazonaws.com/AWSServiceRoleForAmazonQDeveloper",
          "arn:aws:iam::773235999227:role/aws-service-role/notifications.amazonaws.com/AWSServiceRoleForAwsUserNotifications",
          "arn:aws:iam::773235999227:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache",
          "arn:aws:iam::773235999227:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
          "arn:aws:iam::773235999227:role/aws-service-role/organizations.amazonaws.com/AWSServiceRoleForOrganizations",
          "arn:aws:iam::773235999227:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
          "arn:aws:iam::773235999227:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
        ]
      },
      "Action": [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "kms:GrantIsForAWSResource": "true"
        }
      }
    }
  ]
}
```

---

## 📊 O que Esta Política Significa

### ✅ Permissões Habilitadas

| Serviço | O que pode fazer | Status |
|---------|-----------------|--------|
| **ECS** | Criar/gerenciar containers | ✅ Habilitado |
| **RDS** | Criar/gerenciar bancos de dados | ✅ Habilitado |
| **ElastiCache** | Gerenciar cache Redis | ✅ Habilitado |
| **ELB** | Load balancer | ✅ Habilitado |
| **Organizations** | Gerenciar organização AWS | ✅ Habilitado |
| **Resource Explorer** | Explorar recursos | ✅ Habilitado |
| **SQS** | Queue (precisa adicionar) | ⏳ Veremos abaixo |

---

## 🚀 Próximo Passo: Adicionar suas Credenciais

Agora que você sabe que sua conta está configurada com KMS, vamos adicionar suas credenciais pessoais:

### Etapas:

1. **Obtenha seu Access Key ID e Secret Access Key:**
   - Vá para AWS Console: https://console.aws.amazon.com
   - IAM → Users → Seu Usuário
   - Security Credentials → Create access key
   - Selecione: "Command Line Interface (CLI)"
   - Copie os dois valores

2. **Configure localmente:**
   ```powershell
   .\scripts\setup-aws-credentials.ps1
   ```

3. **Suas credenciais serão:**
   - Salvas em: `%USERPROFILE%\.aws\credentials`
   - Integradas com a política KMS existente
   - Prontas para deployment

---

## 🔗 Como as Credenciais se Conectam à Política KMS

```
Seu Access Key ID + Secret Key
        ↓
Autenticado na Conta 773235999227
        ↓
Herda permissões via IAM User
        ↓
Acessa recursos protegidos por KMS
        ↓
ECS, RDS, ElastiCache, SQS funcionam
        ↓
✅ Deployment pronto!
```

---

## 📝 Nota Importante

A política KMS já está configurada com múltiplos roles de serviço AWS. Suas credenciais pessoais irão:

- ✅ Herdar as permissões definidas nesta política
- ✅ Ter acesso completo aos recursos necessários
- ✅ Funcionar com ECS, RDS, ElastiCache, ELB
- ✅ Permitir deployment do YSH B2B

Você **NÃO precisa** editar esta política. Está tudo pronto!

---

## 📋 Checklist

- [ ] Entendi que a conta é `773235999227`
- [ ] Entendi que KMS está pré-configurado
- [ ] Vou obter meu Access Key ID
- [ ] Vou obter meu Secret Access Key
- [ ] Vou executar `.\scripts\setup-aws-credentials.ps1`
- [ ] Vou validar com `aws sts get-caller-identity`
- [ ] Pronto para deploy!

---

## 🎯 Próximo Comando

Quando estiver pronto com suas credenciais:

```powershell
.\scripts\setup-aws-credentials.ps1
```

Isso configurará tudo automaticamente!

---

**Referência:** KMS Key Policy (key-consolepolicy-3)  
**Conta:** 773235999227  
**Status:** ✅ Pronto para deployment YSH B2B
