# 🔐 SETUP AWS - INSTRUÇÕES PASSO A PASSO

Write-Host @"

╔════════════════════════════════════════════════════════════════════════════╗
║           📋 AWS CREDENTIALS SETUP - INSTRUÇÕES VISUAIS                    ║
╚════════════════════════════════════════════════════════════════════════════╝

OPÇÃO 1: CONFIGURAÇÃO INTERATIVA (RECOMENDADO)
═══════════════════════════════════════════════════════════════════════════════

  .\scripts\setup-aws-credentials.ps1

  O script irá:
    ✓ Solicitar Access Key ID
    ✓ Solicitar Secret Access Key
    ✓ Definir região (us-east-1 recomendado)
    ✓ Validar as credenciais
    ✓ Salvar em ~/.aws/credentials


OPÇÃO 2: CONFIGURAÇÃO MANUAL
═══════════════════════════════════════════════════════════════════════════════

  aws configure

  Quando solicitado, insira:
    AWS Access Key ID [None]:          → Sua Access Key ID
    AWS Secret Access Key [None]:      → Sua Secret Access Key
    Default region name [None]:        → us-east-1
    Default output format [None]:      → json


OBTER CREDENCIAIS AWS
═══════════════════════════════════════════════════════════════════════════════

  Se ainda não possui credenciais:

  1. Acesse AWS Console: https://console.aws.amazon.com
  2. Vá para IAM → Users → Seu Usuário
  3. Clique em "Security Credentials"
  4. Em "Access keys", clique "Create access key"
  5. Selecione "Command Line Interface (CLI)"
  6. Copie Access Key ID e Secret Access Key
  7. Cole nos prompts do setup


APÓS CONFIGURAÇÃO
═══════════════════════════════════════════════════════════════════════════════

  Execute os próximos passos:

  1️⃣  Validar conectividade:
      node scripts/test-connectivity.js

  2️⃣  Verificar setup:
      node scripts/verify-aws-setup.js

  3️⃣  Deploy stack:
      .\aws-cloudformation\deploy-stack.ps1


VALIDAÇÃO RÁPIDA
═══════════════════════════════════════════════════════════════════════════════

  aws sts get-caller-identity

  Se funcionar, você verá seu Account ID, User ARN e Timestamp


TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

  ❌ "Unable to locate credentials"
     → Execute o setup-aws-credentials.ps1 ou aws configure

  ❌ "InvalidSignatureException"
     → As credenciais estão incorretas
     → Revise a Access Key ID e Secret Access Key

  ❌ "AccessDenied"
     → As credenciais não têm permissões suficientes
     → Use uma chave com permissões IAM admin


ARQUIVOS DE CONFIGURAÇÃO
═══════════════════════════════════════════════════════════════════════════════

  Credenciais:  ~/.aws/credentials
  Config:       ~/.aws/config

  No Windows:
    %USERPROFILE%\.aws\credentials
    %USERPROFILE%\.aws\config

  ⚠️  Nunca compartilhe estes arquivos!


" -ForegroundColor Cyan

Write-Host "Pressione ENTER para continuar..." -ForegroundColor Yellow
Read-Host
