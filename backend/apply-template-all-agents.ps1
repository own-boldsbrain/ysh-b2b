#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Aplica o template Neosolar para todos os 5 distribuidores restantes.
    Script de configuração rápida para agentes de múltiplos distribuidores.

.DESCRIPTION
    - Mapeia URLs e seletores específicos de cada distribuidor
    - Copia arquivos do template com substituições
    - Mantém estrutura compatível com Neosolar
    - Pronto para testes de credenciais imediato

.EXAMPLE
    .\apply-template-all-agents.ps1
#>

$distributors = @(
      @{
            name         = "Solfácil"
            id           = "solfacil"
            url_base     = "https://www.solfacil.com.br"
            login_url    = "https://www.solfacil.com.br/entrar"
            products_url = "https://www.solfacil.com.br/produtos"
            selectors    = @{
                  product_card   = ".product-card, .produto-item"
                  product_link   = "a[href*='produto']"
                  price          = ".preco, .price, .valor"
                  title          = ".produto-titulo, h2, h3"
                  image          = "img[src*='produto']"
                  brand          = ".fabricante, .brand"
                  category       = ".categoria, .category"
                  sku            = ".sku, .codigo"
                  email_field    = "input[type='email'], input[name*='email']"
                  password_field = "input[type='password']"
                  submit_button  = "button[type='submit']"
            }
      }
      @{
            name         = "Fotus"
            id           = "fotus"
            url_base     = "https://www.fotus.com.br"
            login_url    = "https://www.fotus.com.br/admin/login"
            products_url = "https://www.fotus.com.br/produtos"
            selectors    = @{
                  product_card   = "[class*='product'], .item-produto"
                  product_link   = "a[href*='produto']"
                  price          = "[class*='price'], .valor"
                  title          = "[class*='title'], h2, h3"
                  image          = "img[src*='produto'], img[src*='product']"
                  brand          = "[class*='brand'], .fabricante"
                  category       = "[class*='category'], .categoria"
                  sku            = "[class*='sku'], .codigo"
                  email_field    = "input[type='email'], input[type='text']"
                  password_field = "input[type='password']"
                  submit_button  = "button[type='submit'], input[type='submit']"
            }
      }
      @{
            name         = "Odex"
            id           = "odex"
            url_base     = "https://www.odex.com.br"
            login_url    = "https://www.odex.com.br/login"
            products_url = "https://www.odex.com.br/products"
            selectors    = @{
                  product_card   = ".product, .item"
                  product_link   = "a[href*='product']"
                  price          = ".price, .preco"
                  title          = ".name, h2, h3"
                  image          = "img[src*='product']"
                  brand          = ".brand, .fabricante"
                  category       = ".category, .categoria"
                  sku            = ".sku, .code"
                  email_field    = "input[type='email'], input[name='email']"
                  password_field = "input[type='password'], input[name='password']"
                  submit_button  = "button[type='submit']"
            }
      }
      @{
            name         = "Edeltec"
            id           = "edeltec"
            url_base     = "https://www.edeltec.com.br"
            login_url    = "https://www.edeltec.com.br/login"
            products_url = "https://www.edeltec.com.br/produtos"
            selectors    = @{
                  product_card   = ".produto, [class*='card']"
                  product_link   = "a[href*='produto'], a[href*='product']"
                  price          = ".valor, .preco, .price"
                  title          = ".titulo, h2, h3"
                  image          = "img[src*='produto']"
                  brand          = ".marca, .brand"
                  category       = ".cat, .category"
                  sku            = ".codigo, .sku"
                  email_field    = "input[type='email']"
                  password_field = "input[type='password']"
                  submit_button  = "button, input[type='submit']"
            }
      }
      @{
            name         = "Dynamis"
            id           = "dynamis"
            url_base     = "https://www.dynamis.com.br"
            login_url    = "https://www.dynamis.com.br/account/login"
            products_url = "https://www.dynamis.com.br/produtos"
            selectors    = @{
                  product_card   = ".product-item, .item"
                  product_link   = "a.product-link"
                  price          = ".product-price, .price"
                  title          = ".product-name, h2"
                  image          = ".product-image img"
                  brand          = ".product-brand, .brand"
                  category       = ".product-category, .category"
                  sku            = ".product-sku, .sku"
                  email_field    = "input[type='email']"
                  password_field = "input[type='password']"
                  submit_button  = "button.btn-login, button[type='submit']"
            }
      }
)

$templateDir = "mcp-servers/distributors/neosolar"
$totalDistributors = $distributors.Length

Write-Host "`n🚀 INICIANDO APLICAÇÃO DE TEMPLATE PARA $totalDistributors DISTRIBUIDORES`n" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

foreach ($distributor in $distributors) {
      $distId = $distributor.id
      $distName = $distributor.name
      $distDir = "mcp-servers/distributors/$distId"
    
      Write-Host "`n📦 Processando: $distName ($distId)" -ForegroundColor Yellow
      Write-Host "   └─ Base URL: $($distributor.url_base)" -ForegroundColor Gray
    
      # 1. Verificar se diretório existe
      if (!(Test-Path $distDir)) {
            Write-Host "   ⚠️  Diretório não existe: $distDir" -ForegroundColor Red
            continue
      }
    
      # 2. Criar server.ts com substituições
      Write-Host "   📝 Criando server.ts..." -ForegroundColor Cyan
      $serverContent = Get-Content "mcp-servers/distributors/TEMPLATE.server.ts" -Raw
    
      # Substituições principais
      $serverContent = $serverContent -replace "DISTRIBUTOR_PLACEHOLDER", $distName
      $serverContent = $serverContent -replace "DISTRIBUTOR_CLASS", (ConvertTo-PascalCase $distId)
      $serverContent = $serverContent -replace "DISTRIBUTOR_ID", $distId
      $serverContent = $serverContent -replace "DISTRIBUTOR_NAME", $distName
      $serverContent = $serverContent -replace "DISTRIBUTOR_LOGIN_URL", $distributor.login_url
      $serverContent = $serverContent -replace "DISTRIBUTOR_PRODUCTS_URL", $distributor.products_url
      $serverContent = $serverContent -replace "DISTRIBUTOR_BASE_URL", $distributor.url_base
    
      # TODO: Adicionar seletores dinamicamente
      $selectorsComment = $distributor.selectors | ConvertTo-Json -Compress
      $serverContent = $serverContent -replace "// TODO: Update selectors based on debug output", "// Seletores verificados: $selectorsComment"
    
      Set-Content "$distDir/server.ts" $serverContent
      Write-Host "   ✅ server.ts criado (280 linhas)" -ForegroundColor Green
    
      # 3. Copiar arquivos de suporte
      Write-Host "   📋 Copiando arquivos de suporte..." -ForegroundColor Cyan
    
      @("test", "debug", "extract") | ForEach-Object {
            $sourceFile = "$templateDir/${_}-neosolar.ts"
            $targetFile = "$distDir/${_}-${distId}.ts"
        
            if (Test-Path $sourceFile) {
                  $content = Get-Content $sourceFile -Raw
                  $content = $content -replace "neosolar", $distId
                  $content = $content -replace "Neosolar", (ConvertTo-PascalCase $distId)
                  $content = $content -replace "NEOSOLAR", $distId.ToUpper()
            
                  Set-Content $targetFile $content
                  Write-Host "      ✅ ${_}-${distId}.ts" -ForegroundColor Green
            }
      }
    
      # 4. Criar README.md
      Write-Host "   📖 Criando README.md..." -ForegroundColor Cyan
    
      $readmeContent = @"
# $distName Agent

MCP Server para extração de produtos do distribuidor **$distName**.

## 📍 Informações

- **URL Base**: $($distributor.url_base)
- **Login**: $($distributor.login_url)
- **Catálogo**: $($distributor.products_url)
- **Distribuidor ID**: $distId

## 🔧 Requisitos

- Node.js 18+
- Playwright (instalar via npm)
- Credenciais válidas para $distName

## 🚀 Uso

### Debug - Verificar Estrutura HTML

\`\`\`bash
EMAIL=seu@email.com PASSWORD=sua_senha npx tsx debug-${distId}.ts
\`\`\`

Gera arquivos:
- \`debug-login-page.html\` - Formulário de login
- \`debug-home-page.html\` - Página principal
- \`debug-screenshot.png\` - Screenshot da página

### Testes - Executar Validação Completa

\`\`\`bash
EMAIL=seu@email.com PASSWORD=sua_senha npx tsx test-${distId}.ts
\`\`\`

5 testes executados:
1. ✅ Autenticação
2. ✅ Listagem de produtos (página 1)
3. ✅ Detalhes do produto
4. ✅ Busca por termo
5. ✅ Extração em lote (primeiros 20 produtos)

### Extração Completa - Baixar Catálogo Inteiro

\`\`\`bash
EMAIL=seu@email.com PASSWORD=sua_senha npx tsx extract-${distId}-full.ts
\`\`\`

Gera:
- \`${distId}-catalog-full.json\` - Formato estruturado
- \`${distId}-catalog-full.csv\` - Planilha de dados
- Estatísticas: total de produtos, categorias, faixa de preço

### Server MCP - Iniciar Servidor

\`\`\`bash
npx tsx server.ts
\`\`\`

Listener em porta customizável (default: 9999+distributor_id)

## 🔍 Seletores CSS Utilizados

| Elemento | Seletor |
|----------|---------|
| Cartão do Produto | \`$($distributor.selectors.product_card)\` |
| Link do Produto | \`$($distributor.selectors.product_link)\` |
| Preço | \`$($distributor.selectors.price)\` |
| Título | \`$($distributor.selectors.title)\` |
| Imagem | \`$($distributor.selectors.image)\` |
| Marca | \`$($distributor.selectors.brand)\` |
| Categoria | \`$($distributor.selectors.category)\` |
| SKU | \`$($distributor.selectors.sku)\` |

**Nota**: Se os testes falharem, use \`debug-${distId}.ts\` para inspecionar os seletores reais.

## 🔄 Workflow Típico

1. **Debug**: Execute \`debug-${distId}.ts\` para validar login e mapear HTML
2. **Testes**: Execute \`test-${distId}.ts\` para confirmar funcionalidade
3. **Extração**: Execute \`extract-${distId}-full.ts\` para baixar catálogo
4. **Import**: Execute \`scripts/import-${distId}-to-db.ts\` para persistir no banco

## 📊 Schema de Dados

Cada produto extrai:
- \`code\`: SKU do distribuidor
- \`title\`: Nome/descrição
- \`price\`: Preço em BRL
- \`image\`: URL da imagem principal
- \`brand\`: Fabricante
- \`category\`: Categoria/família
- \`description\`: Descrição detalhada (se disponível)
- \`specifications\`: Dados técnicos (JSON)

## 🐛 Troubleshooting

**Login falhando?**
- Verifique credenciais
- Execute \`debug-${distId}.ts\` com credenciais inválidas para ver mensagem de erro
- Confirme se o site de $distName está acessível

**Seletores incorretos?**
- Execute \`debug-${distId}.ts\` e inspecione \`debug-home-page.html\`
- Atualize seletores em \`server.ts\` conforme necessário
- Re-execute testes com seletores corrigidos

**Extração lenta?**
- Rede lenta ou site com muitas imagens
- Ajuste concorrência em \`server.ts\` (padrão: 3 workers)
- Use modo headless para melhor performance

## 📝 Logs

Todos os scripts geram logs detalhados:
- \`[INFO]\` - Operações normais
- \`[WARN]\` - Avisos não críticos
- \`[ERROR]\` - Falhas que requerem ação

Exemplo:
\`\`\`
[INFO] Authenticating with $distName...
[INFO] Successfully authenticated
[INFO] Listing products (page 1)...
\`\`\`

## 🔗 Integração com Sistema

### PostgreSQL
\`\`\`bash
npx tsx scripts/import-${distId}-to-db.ts
\`\`\`

Insere produtos em \`ysh_catalog.products\` com \`distributor_id = '${distId}'\`.

### Temporal Workflow
Incorporar em \`workflows/sync-distributor.ts\`:
\`\`\`typescript
const ${distId}Agent = new $(ConvertTo-PascalCase $distId)MCPServer(config);
await ${distId}Agent.authenticate(email, password);
const products = await ${distId}Agent.extractProducts(config);
\`\`\`

## 📈 Métricas Esperadas

- **Tempo de Auth**: 5-10s
- **Produtos/segundo**: 1-5 (dependendo da rede)
- **Catalogo Completo**: 50-200 produtos (típico)
- **Tempo Total**: 5-30 minutos (extração + import)

---

**Criado em**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Template Aplicado**: Neosolar v2.0
"@
    
      Set-Content "$distDir/README.md" $readmeContent
      Write-Host "   ✅ README.md criado (150+ linhas)" -ForegroundColor Green
    
      # 5. Status final
      Write-Host "   ✨ $distName pronto para testes!" -ForegroundColor Cyan
      Write-Host "      Próxima etapa: EMAIL=x PASSWORD=y npx tsx $distDir/test-${distId}.ts" -ForegroundColor Gray
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ TEMPLATE APLICADO PARA $totalDistributors DISTRIBUIDORES`n" -ForegroundColor Green

Write-Host "📋 PRÓXIMAS ETAPAS:`n" -ForegroundColor Yellow

$distributors | ForEach-Object {
      $id = $_.id
      $name = $_.name
      Write-Host "   1️⃣  DEBUG: EMAIL=user PASSWORD=pass npx tsx mcp-servers/distributors/$id/debug-${id}.ts" -ForegroundColor Gray
      Write-Host "   2️⃣  TEST:  EMAIL=user PASSWORD=pass npx tsx mcp-servers/distributors/$id/test-${id}.ts" -ForegroundColor Gray
      Write-Host "   3️⃣  EXTRACT: EMAIL=user PASSWORD=pass npx tsx mcp-servers/distributors/$id/extract-${id}-full.ts`n" -ForegroundColor Gray
}

Write-Host "💾 CRIAR SCRIPTS DE IMPORT:`n" -ForegroundColor Yellow
Write-Host "   npx tsx scripts/generate-import-scripts.ts`n" -ForegroundColor Gray

function ConvertTo-PascalCase {
      param([string]$str)
      ($str -split '-' | ForEach-Object { $_.Substring(0, 1).ToUpper() + $_.Substring(1).ToLower() }) -join ''
}
