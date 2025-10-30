# 🔑 Guia Completo: Obter APIs Meta Commerce Platform

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

- ✅ Conta Facebook pessoal ativa
- ✅ Página do Facebook para sua empresa (YSH Solar)
- ✅ Conta no Facebook Business Manager
- ✅ Permissão de administrador na página
- ✅ CNPJ válido (para verificação empresarial)

---

## 🎯 Passo 1: Criar/Acessar Facebook Business Manager

### 1.1 Acesse o Business Manager

1. Vá para: https://business.facebook.com
2. Clique em **"Criar conta"** (se não tiver) ou **"Fazer login"**
3. Use suas credenciais do Facebook pessoal

### 1.2 Configure sua Empresa

Se for primeira vez:

1. Clique em **"Criar conta"**
2. Preencha os dados:
   - **Nome da empresa**: Yello Solar Hub BR (ou YSH Solar)
   - **Seu nome**: [Seu nome completo]
   - **Email comercial**: contato@ysh.solar
3. Clique em **"Enviar"**

### 1.3 Adicione sua Página do Facebook

1. No menu lateral, clique em **"Páginas"**
2. Clique em **"Adicionar"** → **"Adicionar uma página"**
3. Selecione sua página do Facebook (YSH Solar / Yello Solar Hub BR)
4. Clique em **"Adicionar página"**

**✅ Checkpoint**: Você deve ver sua página listada em "Páginas"

---

## 🎯 Passo 2: Criar App no Meta for Developers

### 2.1 Acesse o Portal de Desenvolvedores

1. Vá para: https://developers.facebook.com
2. Faça login com sua conta Facebook
3. No canto superior direito, clique em **"Meus Apps"**

### 2.2 Crie um Novo App

1. Clique no botão **"Criar App"**
2. Selecione o tipo: **"Empresa"** (Business)
3. Clique em **"Avançar"**

### 2.3 Configure o App

Preencha os dados:

- **Nome de exibição do app**: YSH Solar Commerce API
- **Email de contato do app**: dev@ysh.solar (ou seu email)
- **Conta do Business Manager**: Selecione "Yello Solar Hub BR"
- **Finalidade do app**: Selecione "Você mesmo ou sua própria empresa"

Clique em **"Criar app"**

### 2.4 Complete a Verificação de Segurança

- Resolva o CAPTCHA
- Confirme sua senha do Facebook se solicitado

**✅ Checkpoint**: Você foi redirecionado para o painel do app

---

## 🎯 Passo 3: Adicionar Produtos ao App

### 3.1 Adicione a API do Commerce

1. No painel do app, procure por **"Commerce"** na seção "Adicionar produtos"
2. Clique em **"Configurar"** no card do **"Commerce Manager"**
3. Siga o assistente de configuração

### 3.2 Configure Permissões

1. Vá para **"Configurações" → "Básico"** no menu lateral
2. Role até **"Domínios do app"**
3. Adicione seu domínio: `ysh.solar` (ou seu domínio de produção)
4. Clique em **"Salvar alterações"**

### 3.3 Configure URLs de Redirecionamento OAuth

1. Na mesma página, procure **"URLs válidas de redirecionamento do OAuth"**
2. Adicione:
   ```
   https://ysh.solar/auth/facebook/callback
   https://localhost:8080/auth/facebook/callback
   ```
3. Clique em **"Salvar alterações"**

**✅ Checkpoint**: Produtos Commerce configurados

---

## 🎯 Passo 4: Criar Catálogo de Produtos

### 4.1 Acesse o Commerce Manager

1. Vá para: https://business.facebook.com/commerce
2. Ou clique em **"Commerce Manager"** no menu do Business Manager

### 4.2 Crie um Novo Catálogo

1. Clique no botão **"Criar catálogo"**
2. Selecione **"Comércio eletrônico"** (E-commerce)
3. Clique em **"Avançar"**

### 4.3 Configure o Catálogo

Conforme a imagem que você compartilhou:

**Tipo de catálogo:**
- Selecione: **"Produtos online"** ✅

**Conectar-se a uma plataforma de parceiro:**
- ❌ NÃO marque esta opção (vamos usar API customizada)

**Portfólio empresarial:**
- Selecione: **"Yello Solar Hub BR"** (ou o nome da sua empresa)

**Dar acesso às pessoas:**
- ✅ Marque esta opção
- "Os usuários da empresa terão acesso total automático a este catálogo"

**Nome:**
- Digite: `Catalog_Products` (ou como preferir: "YSH Solar - Catálogo Principal")

### 4.4 Finalize a Criação

1. Revise os **Termos do Catálogo**: https://www.facebook.com/policies/commerce/terms
2. Revise as **Políticas de Publicidade**: https://www.facebook.com/policies/ads
3. Revise as **Políticas Comerciais**: https://www.facebook.com/policies/commerce
4. Marque a caixa confirmando que leu as políticas
5. Clique em **"Avançar"**

### 4.5 Anote o ID do Catálogo

Após criação, você será redirecionado para o painel do catálogo:

1. Na URL do navegador, você verá algo como:
   ```
   https://business.facebook.com/commerce/catalogs/1234567890123456/products
   ```
2. O número `1234567890123456` é seu **CATALOG_ID**
3. **COPIE E GUARDE** este número

**✅ Checkpoint**: Catálogo criado com ID disponível

---

## 🎯 Passo 5: Obter Access Token (Token de Acesso)

### 5.1 Acesse o Graph API Explorer

1. Vá para: https://developers.facebook.com/tools/explorer
2. Você será redirecionado para o Graph API Explorer

### 5.2 Configure o Explorer

1. No canto superior direito, clique no dropdown **"Meta App"**
2. Selecione o app que você criou: **"YSH Solar Commerce API"**
3. No dropdown **"User or Page"**, mantenha **"User Token"**

### 5.3 Adicione Permissões

1. Clique no botão **"Permissions"** (ou "Permissões")
2. Marque as seguintes permissões:

   **OBRIGATÓRIAS:**
   - ✅ `catalog_management` - Gerenciar catálogos de produtos
   - ✅ `pages_read_engagement` - Ler engajamento de páginas
   - ✅ `pages_manage_metadata` - Gerenciar metadados de páginas
   - ✅ `business_management` - Gerenciar negócios

   **RECOMENDADAS:**
   - ✅ `ads_management` - Para integração futura com anúncios
   - ✅ `pages_show_list` - Listar páginas

3. Clique em **"Generate Access Token"** (ou "Gerar token de acesso")

### 5.4 Autorize as Permissões

1. Uma janela popup será aberta
2. Revise as permissões solicitadas
3. Clique em **"Continuar como [Seu Nome]"**
4. Selecione a página **"Yello Solar Hub BR"**
5. Clique em **"Avançar"**
6. Revise e clique em **"Concluir"**

### 5.5 Copie o Token de Curta Duração

1. O token aparecerá no campo **"Access Token"**
2. **COPIE** este token (parece com: `EAABwzLixnjYBO...`)
3. Este é um **token de curta duração** (expira em 1-2 horas)

### 5.6 Teste o Token

Para testar, execute no Graph API Explorer:

```
GET /me?fields=id,name
```

Deve retornar seus dados pessoais.

**✅ Checkpoint**: Token de curta duração obtido

---

## 🎯 Passo 6: Converter para Token de Longa Duração

### 6.1 Use a Ferramenta de Debug de Token

1. Vá para: https://developers.facebook.com/tools/debug/accesstoken
2. Cole o token de curta duração no campo
3. Clique em **"Debug"**

### 6.2 Estenda o Token

Na página de debug:

1. Clique no botão **"Extend Access Token"** (no final da página)
2. Um novo token será gerado (este dura **60 dias**)
3. **COPIE** o novo token

### 6.3 Método Alternativo via API

Ou use este comando cURL:

```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=SEU_APP_ID" \
  -d "client_secret=SEU_APP_SECRET" \
  -d "fb_exchange_token=TOKEN_CURTA_DURACAO"
```

**Onde obter App ID e App Secret:**

1. Vá para: https://developers.facebook.com/apps
2. Selecione seu app **"YSH Solar Commerce API"**
3. Clique em **"Configurações" → "Básico"**
4. **App ID**: Está logo no topo
5. **App Secret**: Clique em **"Mostrar"** → Digite sua senha → Copie

### 6.4 Obter Token Permanente (Opcional)

Para um token que nunca expira (Page Access Token):

1. No Graph API Explorer, mude para **"User or Page" → "Get Page Access Token"**
2. Selecione sua página **"Yello Solar Hub BR"**
3. Copie o novo token gerado
4. Este token **não expira** enquanto você tiver permissões na página

**✅ Checkpoint**: Token de longa duração obtido

---

## 🎯 Passo 7: Verificar Permissões do Token

### 7.1 Inspecione o Token

1. Vá para: https://developers.facebook.com/tools/debug/accesstoken
2. Cole seu token de longa duração
3. Clique em **"Debug"**

### 7.2 Verifique as Informações

Confirme:

- **Type**: User (ou Page se for Page Token)
- **App**: YSH Solar Commerce API
- **Valid**: ✅ True
- **Expires**: Data futura (ou "Never" para Page Token)
- **Scopes**: Deve listar todas as permissões que você autorizou

### 7.3 Teste Acesso ao Catálogo

Execute no Graph API Explorer:

```
GET /{CATALOG_ID}?fields=id,name,product_count
```

Substitua `{CATALOG_ID}` pelo ID que você anotou no Passo 4.

**Resposta esperada:**

```json
{
  "id": "1234567890123456",
  "name": "Catalog_Products",
  "product_count": 0
}
```

**✅ Checkpoint**: Token validado e testado

---

## 🎯 Passo 8: Configurar no Sistema YSH

### 8.1 Copie o Arquivo de Ambiente

```bash
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\data-pipeline
cp .env.example .env
```

### 8.2 Edite o Arquivo .env

Abra `.env` e preencha:

```bash
# ============================================================================
# META COMMERCE PLATFORM
# ============================================================================

# ID do catálogo do Commerce Manager (número de 16 dígitos)
# Encontre em: https://business.facebook.com/commerce/catalogs
FACEBOOK_CATALOG_ID=1234567890123456

# Access Token de longa duração do Graph API
# Obtenha em: https://developers.facebook.com/tools/explorer
# Permissões necessárias: catalog_management, pages_manage_metadata
FACEBOOK_ACCESS_TOKEN=EAABwzLixnjYBO...seu_token_aqui...

# App ID do Facebook (encontre em Settings → Basic)
FACEBOOK_APP_ID=987654321098765

# App Secret do Facebook (encontre em Settings → Basic → Show)
FACEBOOK_APP_SECRET=abcdef1234567890abcdef1234567890

# ID da sua Página do Facebook (encontre na URL da página)
FACEBOOK_PAGE_ID=1234567890

# URL base para produtos no seu site (usado no campo 'link')
BASE_PRODUCT_URL=https://ysh.solar/produtos

# API Version (recomendado: v18.0 ou superior)
FACEBOOK_API_VERSION=v18.0

# Rate limiting (requisições por hora)
FACEBOOK_API_RATE_LIMIT=200
```

### 8.3 Salve e Proteja o Arquivo

```bash
# Adicione .env ao .gitignore (se ainda não estiver)
echo ".env" >> .gitignore

# Defina permissões restritas (somente você pode ler)
icacls .env /inheritance:r /grant:r "$env:USERNAME:F"
```

**⚠️ IMPORTANTE**: Nunca commite o arquivo `.env` para o Git!

**✅ Checkpoint**: Credenciais configuradas no sistema

---

## 🎯 Passo 9: Testar a Integração

### 9.1 Teste de Conexão

Crie um script de teste:

```python
# test_meta_connection.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CATALOG_ID = os.getenv('FACEBOOK_CATALOG_ID')
ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v18.0')

url = f"https://graph.facebook.com/{API_VERSION}/{CATALOG_ID}"
params = {
    'fields': 'id,name,product_count,business',
    'access_token': ACCESS_TOKEN
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    print("✅ Conexão bem-sucedida!")
else:
    print("❌ Erro na conexão!")
    print(f"Mensagem: {response.json().get('error', {}).get('message')}")
```

Execute:

```bash
python test_meta_connection.py
```

### 9.2 Teste de Upload de Produto

```python
# test_product_upload.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CATALOG_ID = os.getenv('FACEBOOK_CATALOG_ID')
ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v18.0')

# Produto de teste
product_data = {
    'retailer_id': 'TEST-001',
    'title': 'Painel Solar Teste 450W',
    'description': 'Painel solar fotovoltaico de teste',
    'availability': 'in stock',
    'condition': 'new',
    'price': '1500.00 BRL',
    'link': 'https://ysh.solar/produtos/test-001',
    'image_link': 'https://ysh.solar/images/test-001.jpg',
    'brand': 'YSH Test',
    'google_product_category': 'Electronics > Components > Solar Panels',
}

url = f"https://graph.facebook.com/{API_VERSION}/{CATALOG_ID}/products"
data = {
    'access_token': ACCESS_TOKEN,
    'requests': [{
        'method': 'CREATE',
        'data': product_data
    }]
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    print("✅ Produto criado com sucesso!")
else:
    print("❌ Erro ao criar produto!")
```

Execute:

```bash
python test_product_upload.py
```

### 9.3 Verifique no Commerce Manager

1. Vá para: https://business.facebook.com/commerce
2. Selecione seu catálogo **"Catalog_Products"**
3. Você deve ver o produto de teste listado

**✅ Checkpoint**: Integração testada e funcionando

---

## 🎯 Passo 10: Configuração de Produção

### 10.1 Configure Webhooks (Opcional)

Para receber notificações de mudanças:

1. No painel do app (developers.facebook.com)
2. Vá para **"Produtos" → "Webhooks"**
3. Clique em **"Adicionar inscrição"**
4. Selecione **"catalog_management"**
5. Configure a URL de callback: `https://ysh.solar/webhooks/facebook`

### 10.2 Configure Políticas de Privacidade

1. No painel do app, vá para **"Configurações" → "Básico"**
2. Adicione:
   - **URL da Política de Privacidade**: https://ysh.solar/privacidade
   - **URL dos Termos de Serviço**: https://ysh.solar/termos

### 10.3 Solicite Revisão do App (Para Produção)

Se for usar em produção com muitos usuários:

1. Vá para **"Revisão do App"**
2. Solicite permissões avançadas
3. Envie documentação da sua empresa
4. Aguarde aprovação (2-5 dias úteis)

### 10.4 Configure Alertas de Segurança

1. Vá para **"Business Manager" → "Configurações"**
2. Clique em **"Notificações"**
3. Ative alertas para:
   - Mudanças de permissões
   - Atividade suspeita
   - Expiração de tokens

**✅ Checkpoint**: Configuração de produção completa

---

## 📊 Resumo das Credenciais Obtidas

Ao final deste processo, você terá:

| Credencial | Onde Obter | Onde Usar |
|------------|------------|-----------|
| **FACEBOOK_CATALOG_ID** | Commerce Manager → URL do catálogo | `.env` |
| **FACEBOOK_ACCESS_TOKEN** | Graph API Explorer → Generate Token | `.env` |
| **FACEBOOK_APP_ID** | App Dashboard → Settings → Basic | `.env` |
| **FACEBOOK_APP_SECRET** | App Dashboard → Settings → Basic | `.env` |
| **FACEBOOK_PAGE_ID** | URL da sua página do Facebook | `.env` |

---

## 🔄 Manutenção de Tokens

### Renovação Automática

Os tokens de longa duração expiram em **60 dias**. Configure renovação automática:

```python
# scripts/renew_facebook_token.py
import os
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

APP_ID = os.getenv('FACEBOOK_APP_ID')
APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
OLD_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

url = "https://graph.facebook.com/v18.0/oauth/access_token"
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': APP_ID,
    'client_secret': APP_SECRET,
    'fb_exchange_token': OLD_TOKEN
}

response = requests.get(url, params=params)
if response.status_code == 200:
    new_token = response.json()['access_token']
    
    # Atualiza .env
    set_key('.env', 'FACEBOOK_ACCESS_TOKEN', new_token)
    print(f"✅ Token renovado com sucesso!")
    print(f"Novo token: {new_token[:50]}...")
else:
    print(f"❌ Erro ao renovar token: {response.json()}")
```

Agende via cron (Linux) ou Task Scheduler (Windows):

```bash
# Executar todo dia 1º do mês
0 0 1 * * python /path/to/renew_facebook_token.py
```

---

## 🆘 Troubleshooting

### Erro: "Invalid OAuth access token"

**Causa**: Token expirado ou inválido

**Solução**:
1. Gere um novo token no Graph API Explorer
2. Converta para longa duração
3. Atualize o `.env`

### Erro: "Catalog not found"

**Causa**: ID do catálogo incorreto

**Solução**:
1. Vá para Commerce Manager
2. Copie o ID da URL novamente
3. Verifique se não tem espaços extras

### Erro: "Insufficient permissions"

**Causa**: Token sem permissões necessárias

**Solução**:
1. No Graph API Explorer, clique em "Permissions"
2. Adicione `catalog_management` e `pages_manage_metadata`
3. Gere novo token

### Erro: "Image URL must be HTTPS"

**Causa**: URLs de imagem com HTTP

**Solução**:
1. Configure SSL/TLS no seu servidor
2. Use CloudFlare ou AWS CloudFront
3. Certifique-se que `BASE_PRODUCT_URL` use HTTPS

### Erro: "Rate limit exceeded"

**Causa**: Muitas requisições em curto período

**Solução**:
1. Aumente intervalos entre requisições
2. Use batch API (até 100 produtos por vez)
3. Configure `FACEBOOK_API_RATE_LIMIT=50` no `.env`

---

## 📚 Referências Oficiais

- **Meta Commerce Platform Docs**: https://developers.facebook.com/docs/commerce-platform
- **Graph API Reference**: https://developers.facebook.com/docs/graph-api
- **Catalog API**: https://developers.facebook.com/docs/marketing-api/catalog
- **Business Manager**: https://business.facebook.com
- **Developer Portal**: https://developers.facebook.com

---

## ✅ Checklist Final

Antes de ir para produção, verifique:

- [ ] Catálogo criado no Commerce Manager
- [ ] App configurado no Meta for Developers
- [ ] Token de longa duração obtido e testado
- [ ] Arquivo `.env` preenchido corretamente
- [ ] Script de teste executado com sucesso
- [ ] Produto de teste aparecendo no Commerce Manager
- [ ] URLs de produtos com HTTPS configurado
- [ ] Política de privacidade publicada
- [ ] Renovação automática de token configurada
- [ ] Monitoramento de erros ativo (Sentry/Prometheus)
- [ ] Backup das credenciais em local seguro
- [ ] Documentação interna atualizada

---

**🎉 Parabéns! Você configurou com sucesso a integração com Meta Commerce Platform!**

Próximos passos: Execute o data pipeline completo com `docker-compose up -d`
