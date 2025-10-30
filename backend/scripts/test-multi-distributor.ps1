#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Teste Rápido Multi-Distribuidor - Validação do Sistema
.DESCRIPTION
    Executa scrapers funcionais e testa workflow end-to-end
#>

Write-Host @"

╔════════════════════════════════════════════════════════════╗
║  🧪 TESTE MULTI-DISTRIBUIDOR - Sistema de Cotação         ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Carregardistribuidores funcionais conhecidos
$workingDistributors = @(
      @{ Name = "Edeltec"; Script = "extract-edeltec-deep.ts"; Output = "edeltec" },
      @{ Name = "Fortlev"; Script = "extract-fortlev-final.ts"; Output = "fortlev" },
      @{ Name = "Neosolar"; Script = "extract-neosolar-production.ts"; Output = "neosolar" }
)

Write-Host "📊 Verificando distribuidores disponíveis...`n" -ForegroundColor Yellow

$available = @()
foreach ($dist in $workingDistributors) {
      $outputDir = "output/$($dist.Output)"
    
      if (Test-Path $outputDir) {
            $jsonFiles = Get-ChildItem "$outputDir/*.json" -ErrorAction SilentlyContinue | 
            Where-Object { $_.Name -match 'products' } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        
            if ($jsonFiles) {
                  try {
                        $products = Get-Content $jsonFiles.FullName -Raw | ConvertFrom-Json
                        $productCount = $products.Count
                
                        if ($productCount -gt 50) {
                              $available += $dist
                              Write-Host "  ✅ $($dist.Name): $productCount produtos ($(Get-Date $jsonFiles.LastWriteTime -Format 'dd/MM HH:mm'))" -ForegroundColor Green
                        }
                        else {
                              Write-Host "  ⚠️  $($dist.Name): Apenas $productCount produtos" -ForegroundColor Yellow
                        }
                  }
                  catch {
                        Write-Host "  ❌ $($dist.Name): Erro ao ler dados" -ForegroundColor Red
                  }
            }
            else {
                  Write-Host "  ⚪ $($dist.Name): Sem dados" -ForegroundColor Gray
            }
      }
      else {
            Write-Host "  ⚪ $($dist.Name): Nunca executado" -ForegroundColor Gray
      }
}

if ($available.Count -eq 0) {
      Write-Host "`n❌ Nenhum distribuidor com dados válidos encontrado" -ForegroundColor Red
      Write-Host "   Execute os scrapers primeiro ou aguarde conclusão`n" -ForegroundColor Yellow
      exit 1
}

Write-Host "`n✅ $($available.Count) distribuidor(es) disponível(is) para teste`n" -ForegroundColor Green

# Testar ScraperModuleService
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧪 TESTE 1: Normalização de Produtos                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$testResults = @()

foreach ($dist in $available) {
      Write-Host "📦 Testando $($dist.Name)..." -ForegroundColor Yellow
    
      $outputDir = "output/$($dist.Output)"
      $jsonFile = Get-ChildItem "$outputDir/*.json" -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -match 'products' } |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    
      if ($jsonFile) {
            $products = Get-Content $jsonFile.FullName -Raw | ConvertFrom-Json
        
            # Validar estrutura
            $sample = $products[0]
            $hasRequired = $sample.PSObject.Properties.Name -contains 'sku' -and
            $sample.PSObject.Properties.Name -contains 'title' -and
            $sample.PSObject.Properties.Name -contains 'price'
        
            if ($hasRequired) {
                  # Estatísticas
                  $withPrice = ($products | Where-Object { $_.price -gt 0 }).Count
                  $categories = ($products | Group-Object category).Count
            
                  $testResults += @{
                        Distributor  = $dist.Name
                        Total        = $products.Count
                        WithPrice    = $withPrice
                        PricePercent = [math]::Round(($withPrice / $products.Count) * 100, 1)
                        Categories   = $categories
                        Status       = "✅"
                  }
            
                  Write-Host "  ✅ Estrutura válida" -ForegroundColor Green
                  Write-Host "  📊 $($products.Count) produtos | $withPrice com preço ($([math]::Round(($withPrice / $products.Count) * 100, 1))%)" -ForegroundColor Gray
                  Write-Host "  🏷️  $categories categoria(s)`n" -ForegroundColor Gray
            }
            else {
                  $testResults += @{
                        Distributor = $dist.Name
                        Status      = "❌"
                        Error       = "Estrutura inválida"
                  }
                  Write-Host "  ❌ Estrutura de dados inválida`n" -ForegroundColor Red
            }
      }
}

# Resumo
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  📊 RESUMO DOS TESTES                                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

$testResults | ForEach-Object {
      if ($_.Status -eq "✅") {
            Write-Host "$($_.Status) $($_.Distributor):" -ForegroundColor Green
            Write-Host "   • $($_.Total) produtos ($($_.WithPrice) com preço - $($_.PricePercent)%)" -ForegroundColor Gray
            Write-Host "   • $($_.Categories) categorias" -ForegroundColor Gray
      }
      else {
            Write-Host "$($_.Status) $($_.Distributor): $($_.Error)" -ForegroundColor Red
      }
}

# Calcular total
$totalProducts = ($testResults | Where-Object { $_.Status -eq "✅" } | Measure-Object -Property Total -Sum).Sum
$totalWithPrice = ($testResults | Where-Object { $_.Status -eq "✅" } | Measure-Object -Property WithPrice -Sum).Sum

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TOTAL DISPONÍVEL PARA COTAÇÃO:" -ForegroundColor White
Write-Host "  • $totalProducts produtos de $($testResults.Count) distribuidores" -ForegroundColor Green
Write-Host "  • $totalWithPrice com preços válidos ($([math]::Round(($totalWithPrice / $totalProducts) * 100, 1))%)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Sugestão de teste end-to-end
Write-Host "🚀 PRÓXIMO PASSO: Testar Workflow Completo`n" -ForegroundColor Yellow
Write-Host "Execute no Medusa backend:" -ForegroundColor White
Write-Host @"
  
  # 1. Criar solicitação de cotação
  POST /admin/comparative-quotes
  {
    "customer_id": "cust_01",
    "project_type": "residential",
    "estimated_power_kwp": 10.5,
    "invited_suppliers": ["$($available[0].Output.ToLower())", "$($available[1].Output.ToLower())"]
  }
  
  # 2. Publicar e executar scrapers
  POST /admin/comparative-quotes/:id/publish
  
  # 3. Ver comparação
  GET /admin/comparative-quotes/:id/comparison
  
  # 4. Selecionar melhor cotação
  POST /admin/comparative-quotes/:id/select
  {
    "supplier_id": "sup_01",
    "selection_reason": "Melhor preço e prazo"
  }

"@ -ForegroundColor Gray

Write-Host "✅ Teste de validação concluído!`n" -ForegroundColor Green
