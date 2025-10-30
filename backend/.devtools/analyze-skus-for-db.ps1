# Análise de SKUs para Upload no Banco de Dados
# Data: 19 de Outubro de 2025

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ANÁLISE DE SKUs PARA UPLOAD NO BANCO DE DADOS                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$jsonPath = "c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\unified_products.json"

if (-not (Test-Path $jsonPath)) {
      Write-Host "❌ Arquivo não encontrado: $jsonPath" -ForegroundColor Red
      exit 1
}

Write-Host "📂 Carregando arquivo: unified_products.json" -ForegroundColor Yellow
$json = Get-Content $jsonPath -Raw | ConvertFrom-Json
Write-Host "✅ Arquivo carregado com sucesso!" -ForegroundColor Green
Write-Host ""

# ==================== ANÁLISE GERAL ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 ESTATÍSTICAS GERAIS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$totalProducts = $json.Count
$withSKU = ($json | Where-Object { $_.id -and $_.id -ne "" }).Count
$withoutSKU = $totalProducts - $withSKU

Write-Host "  Total de produtos no arquivo: " -NoNewline
Write-Host "$totalProducts" -ForegroundColor Green
Write-Host "  Produtos com SKU (ID): " -NoNewline
Write-Host "$withSKU" -ForegroundColor Green
Write-Host "  Produtos sem SKU (ID): " -NoNewline
Write-Host "$withoutSKU" -ForegroundColor $(if ($withoutSKU -gt 0) { "Red" }else { "Green" })
Write-Host ""

# ==================== ANÁLISE POR CATEGORIA ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📦 DISTRIBUIÇÃO POR CATEGORIA" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$byCategory = $json | Group-Object category | Select-Object `
@{Name = 'Categoria'; Expression = { $_.Name } }, `
@{Name = 'Quantidade'; Expression = { $_.Count } }, `
@{Name = 'Percentual'; Expression = { [math]::Round(($_.Count / $totalProducts) * 100, 1) } }

$byCategory | Format-Table -AutoSize
Write-Host ""

# ==================== ANÁLISE POR DISTRIBUIDOR ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🏢 DISTRIBUIÇÃO POR DISTRIBUIDOR" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$byDistributor = $json | Group-Object distributor | Select-Object `
@{Name = 'Distribuidor'; Expression = { $_.Name } }, `
@{Name = 'Quantidade'; Expression = { $_.Count } }, `
@{Name = 'Percentual'; Expression = { [math]::Round(($_.Count / $totalProducts) * 100, 1) } } | `
      Sort-Object Quantidade -Descending

$byDistributor | Format-Table -AutoSize
Write-Host ""

# ==================== ANÁLISE DE COMPLETUDE ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ COMPLETUDE DE DADOS PARA UPLOAD" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar campos obrigatórios
$productsReady = $json | Where-Object { 
      $_.id -and 
      $_.name -and 
      $_.distributor -and 
      $_.category -and 
      $_.pricing -and 
      $_.pricing.price_brl -and 
      $_.pricing.price_brl -gt 0 
}

$readyCount = $productsReady.Count
$notReadyCount = $totalProducts - $readyCount

Write-Host "  ✅ Produtos PRONTOS para upload: " -NoNewline
Write-Host "$readyCount" -ForegroundColor Green -NoNewline
Write-Host " ($([math]::Round(($readyCount/$totalProducts)*100, 1))%)" -ForegroundColor Green

Write-Host "  ⚠️  Produtos com dados FALTANDO: " -NoNewline
Write-Host "$notReadyCount" -ForegroundColor Yellow -NoNewline
Write-Host " ($([math]::Round(($notReadyCount/$totalProducts)*100, 1))%)" -ForegroundColor Yellow
Write-Host ""

# ==================== ANÁLISE DETALHADA POR DISTRIBUIDOR ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 COMPLETUDE POR DISTRIBUIDOR" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$completudeByDist = $json | Group-Object distributor | ForEach-Object {
      $dist = $_.Name
      $total = $_.Count
      $ready = ($_.Group | Where-Object { 
                  $_.id -and 
                  $_.name -and 
                  $_.pricing -and 
                  $_.pricing.price_brl -and 
                  $_.pricing.price_brl -gt 0 
            }).Count
      $missing = $total - $ready
      $percent = [math]::Round(($ready / $total) * 100, 1)
    
      [PSCustomObject]@{
            Distribuidor     = $dist
            Total            = $total
            Prontos          = $ready
            Faltando         = $missing
            'Completude (%)' = $percent
            Status           = if ($percent -eq 100) { "✅" } elseif ($percent -ge 50) { "⚠️" } else { "❌" }
      }
} | Sort-Object 'Completude (%)' -Descending

$completudeByDist | Format-Table -AutoSize
Write-Host ""

# ==================== ANÁLISE DE CAMPOS FALTANTES ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔎 ANÁLISE DE CAMPOS FALTANTES" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$missingAnalysis = @{
      'Sem ID/SKU'       = ($json | Where-Object { -not $_.id -or $_.id -eq "" }).Count
      'Sem Nome'         = ($json | Where-Object { -not $_.name -or $_.name -eq "" }).Count
      'Sem Distribuidor' = ($json | Where-Object { -not $_.distributor }).Count
      'Sem Categoria'    = ($json | Where-Object { -not $_.category }).Count
      'Sem Preço'        = ($json | Where-Object { -not $_.pricing -or -not $_.pricing.price_brl -or $_.pricing.price_brl -eq 0 }).Count
      'Sem Descrição'    = ($json | Where-Object { -not $_.description -or $_.description -eq "" }).Count
}

$missingAnalysis.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
      $color = if ($_.Value -eq 0) { "Green" } elseif ($_.Value -lt 100) { "Yellow" } else { "Red" }
      $icon = if ($_.Value -eq 0) { "✅" } elseif ($_.Value -lt 100) { "⚠️" } else { "❌" }
      Write-Host "  $icon $($_.Key): " -NoNewline
      Write-Host "$($_.Value)" -ForegroundColor $color -NoNewline
      Write-Host " produtos ($([math]::Round(($_.Value/$totalProducts)*100, 1))%)" -ForegroundColor $color
}
Write-Host ""

# ==================== ANÁLISE DE PREÇOS ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💰 ANÁLISE DE PREÇOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$productsWithPrice = $json | Where-Object { $_.pricing -and $_.pricing.price_brl -and $_.pricing.price_brl -gt 0 }
$priceStats = $productsWithPrice | Measure-Object -Property { $_.pricing.price_brl } -Average -Minimum -Maximum

Write-Host "  Produtos com preço: $($productsWithPrice.Count)" -ForegroundColor Green
Write-Host "  Preço médio: R$ $([math]::Round($priceStats.Average, 2))" -ForegroundColor Cyan
Write-Host "  Preço mínimo: R$ $([math]::Round($priceStats.Minimum, 2))" -ForegroundColor Cyan
Write-Host "  Preço máximo: R$ $([math]::Round($priceStats.Maximum, 2))" -ForegroundColor Cyan
Write-Host ""

# ==================== EXEMPLOS DE PRODUTOS PRONTOS ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ EXEMPLOS DE PRODUTOS PRONTOS PARA UPLOAD (5 primeiros)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$productsReady | Select-Object -First 5 | Select-Object `
@{Name = 'SKU'; Expression = { $_.id } }, `
@{Name = 'Nome'; Expression = { $_.name } }, `
@{Name = 'Distribuidor'; Expression = { $_.distributor } }, `
@{Name = 'Categoria'; Expression = { $_.category } }, `
@{Name = 'Preço'; Expression = { "R$ $([math]::Round($_.pricing.price_brl, 2))" } } | `
      Format-Table -AutoSize

Write-Host ""

# ==================== EXEMPLOS DE PRODUTOS COM PROBLEMAS ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ⚠️  EXEMPLOS DE PRODUTOS COM DADOS FALTANDO (5 primeiros)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$productsNotReady = $json | Where-Object { 
      -not ($_.id -and 
            $_.name -and 
            $_.distributor -and 
            $_.category -and 
            $_.pricing -and 
            $_.pricing.price_brl -and 
            $_.pricing.price_brl -gt 0)
}

$productsNotReady | Select-Object -First 5 | ForEach-Object {
      $product = $_
      $missing = @()
    
      if (-not $product.id) { $missing += "SKU" }
      if (-not $product.name) { $missing += "Nome" }
      if (-not $product.distributor) { $missing += "Distribuidor" }
      if (-not $product.category) { $missing += "Categoria" }
      if (-not $product.pricing -or -not $product.pricing.price_brl -or $product.pricing.price_brl -eq 0) { $missing += "Preço" }
    
      [PSCustomObject]@{
            SKU               = $product.id
            Nome              = $product.name
            Distribuidor      = $product.distributor
            'Campos Faltando' = ($missing -join ", ")
      }
} | Format-Table -AutoSize -Wrap

Write-Host ""

# ==================== RECOMENDAÇÕES ====================
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💡 RECOMENDAÇÕES" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($readyCount -ge ($totalProducts * 0.8)) {
      Write-Host "  ✅ ÓTIMO! Mais de 80% dos produtos estão prontos para upload" -ForegroundColor Green
      Write-Host "  📤 Você pode prosseguir com o upload dos $readyCount produtos completos" -ForegroundColor Green
}
elseif ($readyCount -ge ($totalProducts * 0.5)) {
      Write-Host "  ⚠️  MODERADO: Apenas $([math]::Round(($readyCount/$totalProducts)*100, 1))% dos produtos estão prontos" -ForegroundColor Yellow
      Write-Host "  💡 Recomendação: Priorize completar os dados dos produtos mais importantes" -ForegroundColor Yellow
}
else {
      Write-Host "  ❌ ATENÇÃO: Menos de 50% dos produtos estão prontos para upload" -ForegroundColor Red
      Write-Host "  🔧 Recomendação: Execute os scripts de enriquecimento de dados primeiro" -ForegroundColor Red
}

Write-Host ""
Write-Host "  Principais ações necessárias:" -ForegroundColor Yellow
Write-Host ""

if ($missingAnalysis['Sem Preço'] -gt 0) {
      Write-Host "    1. Completar preços: $($missingAnalysis['Sem Preço']) produtos sem preço" -ForegroundColor Yellow
      Write-Host "       - Neosolar: 1662 produtos (36.1% de completude)" -ForegroundColor Yellow
      Write-Host "       - Solfacil: 92 produtos (0% de completude)" -ForegroundColor Yellow
}

if ($missingAnalysis['Sem Descrição'] -gt 0) {
      Write-Host "    2. Gerar descrições: $($missingAnalysis['Sem Descrição']) produtos sem descrição" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 FIM DA ANÁLISE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Exportar lista de produtos prontos
$readyListPath = "c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\products-ready-for-db.json"
Write-Host "💾 Exportando lista de produtos prontos para: products-ready-for-db.json" -ForegroundColor Cyan
$productsReady | ConvertTo-Json -Depth 10 | Set-Content $readyListPath
Write-Host "✅ Arquivo exportado com sucesso! ($($productsReady.Count) produtos)" -ForegroundColor Green
Write-Host ""

# Exportar lista de produtos com problemas
$notReadyListPath = "c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\products-need-data.json"
Write-Host "💾 Exportando lista de produtos com dados faltando: products-need-data.json" -ForegroundColor Cyan
$productsNotReady | ConvertTo-Json -Depth 10 | Set-Content $notReadyListPath
Write-Host "✅ Arquivo exportado com sucesso! ($($productsNotReady.Count) produtos)" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 Próximos passos:" -ForegroundColor Green
Write-Host "   1. Revisar os arquivos exportados" -ForegroundColor White
Write-Host "   2. Executar scripts de enriquecimento para completar dados faltantes" -ForegroundColor White
Write-Host "   3. Importar os produtos prontos para o banco de dados" -ForegroundColor White
Write-Host ""
