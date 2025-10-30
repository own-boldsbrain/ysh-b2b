#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Monitor de Scrapers - Acompanha execução em tempo real
.DESCRIPTION
    Script PowerShell para monitorar progresso dos scrapers Odex e Solfácil
    - Monitora criação de arquivos JSON
    - Exibe screenshots gerados
    - Mostra estatísticas em tempo real
    - Alertas de erros
#>

param(
      [int]$IntervalSeconds = 10,
      [int]$MaxMonitoringMinutes = 15
)

$ErrorActionPreference = "SilentlyContinue"

# Diretórios de output
$odexDir = "output/odex-fixed"
$solfacilDir = "output/solfacil-fixed"

# Cores
function Write-ColorOutput {
      param([string]$Message, [string]$Color = "White")
      Write-Host $Message -ForegroundColor $Color
}

function Get-LatestProducts {
      param([string]$Directory)
    
      if (-not (Test-Path $Directory)) {
            return $null
      }
    
      $jsonFiles = Get-ChildItem "$Directory/*.json" -ErrorAction SilentlyContinue | 
      Where-Object { $_.Name -match 'products-.*\.json' } |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    
      if ($jsonFiles) {
            try {
                  $content = Get-Content $jsonFiles.FullName -Raw | ConvertFrom-Json
                  return @{
                        File         = $jsonFiles.Name
                        Count        = $content.Count
                        LastModified = $jsonFiles.LastWriteTime
                        Products     = $content
                  }
            }
            catch {
                  return $null
            }
      }
      return $null
}

function Get-LatestScreenshots {
      param([string]$Directory)
    
      if (-not (Test-Path $Directory)) {
            return @()
      }
    
      return Get-ChildItem "$Directory/*.png" -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 5 Name, LastWriteTime
}

function Show-ScraperStatus {
      param([string]$Name, [string]$Directory)
    
      Write-ColorOutput "`n═══════════════════════════════════════════════════════" "Cyan"
      Write-ColorOutput " 📊 $Name" "Yellow"
      Write-ColorOutput "═══════════════════════════════════════════════════════" "Cyan"
    
      $products = Get-LatestProducts -Directory $Directory
      $screenshots = Get-LatestScreenshots -Directory $Directory
    
      if ($products) {
            Write-ColorOutput "`n✅ Produtos Extraídos: $($products.Count)" "Green"
            Write-ColorOutput "   📄 Arquivo: $($products.File)" "Gray"
            Write-ColorOutput "   🕒 Atualizado: $($products.LastModified.ToString('HH:mm:ss'))" "Gray"
        
            if ($products.Count -gt 0) {
                  # Stats por categoria
                  $categories = $products.Products | Group-Object category
                  Write-ColorOutput "`n   📦 Por Categoria:" "White"
                  foreach ($cat in $categories) {
                        $avgPrice = ($cat.Group | Where-Object { $_.price -gt 0 } | Measure-Object -Property price -Average).Average
                        if ($avgPrice) {
                              Write-ColorOutput "      • $($cat.Name): $($cat.Count) produtos (média R$ $([math]::Round($avgPrice, 2)))" "Gray"
                        }
                        else {
                              Write-ColorOutput "      • $($cat.Name): $($cat.Count) produtos" "Gray"
                        }
                  }
            
                  # Últimos 3 produtos
                  Write-ColorOutput "`n   🔍 Últimos Produtos:" "White"
                  $products.Products | Select-Object -First 3 | ForEach-Object {
                        $priceStr = if ($_.price -gt 0) { "R$ $($_.price)" } else { "Sem preço" }
                        Write-ColorOutput "      • [$($_.sku)] $($_.title.Substring(0, [Math]::Min(50, $_.title.Length)))... - $priceStr" "Gray"
                  }
            }
      }
      else {
            Write-ColorOutput "`n⏳ Aguardando produtos..." "Yellow"
      }
    
      if ($screenshots.Count -gt 0) {
            Write-ColorOutput "`n   📸 Screenshots Recentes:" "White"
            $screenshots | ForEach-Object {
                  Write-ColorOutput "      • $($_.Name) - $($_.LastWriteTime.ToString('HH:mm:ss'))" "Gray"
            }
      }
}

function Check-ProcessRunning {
      param([string]$ProcessPattern)
    
      $processes = Get-Process | Where-Object { 
            $_.ProcessName -like "*node*" -or $_.ProcessName -like "*tsx*" 
      }
    
      return $processes.Count -gt 0
}

# Header
Clear-Host
Write-ColorOutput @"

╔════════════════════════════════════════════════════════════╗
║  🔍 MONITOR DE SCRAPERS - Tempo Real                      ║
║  Odex Fixed + Solfácil Fixed                              ║
╚════════════════════════════════════════════════════════════╝

"@ "Cyan"

Write-ColorOutput "⚙️  Configuração:" "Yellow"
Write-ColorOutput "   • Intervalo: $IntervalSeconds segundos" "Gray"
Write-ColorOutput "   • Duração máxima: $MaxMonitoringMinutes minutos" "Gray"
Write-ColorOutput "   • Diretórios:" "Gray"
Write-ColorOutput "     - Odex: $odexDir" "Gray"
Write-ColorOutput "     - Solfácil: $solfacilDir" "Gray"

$startTime = Get-Date
$iterations = 0
$maxIterations = ($MaxMonitoringMinutes * 60) / $IntervalSeconds

# Loop de monitoramento
while ($iterations -lt $maxIterations) {
      $elapsed = (Get-Date) - $startTime
      $iterations++
    
      Write-ColorOutput "`n`n" "White"
      Write-ColorOutput "════════════════════════════════════════════════════════════" "Cyan"
      Write-ColorOutput " ⏱️  Tempo decorrido: $([math]::Round($elapsed.TotalMinutes, 1)) minutos | Iteração: $iterations/$maxIterations" "White"
      Write-ColorOutput "════════════════════════════════════════════════════════════" "Cyan"
    
      # Status Odex
      Show-ScraperStatus -Name "ODEX FIXED" -Directory $odexDir
    
      # Status Solfácil
      Show-ScraperStatus -Name "SOLFÁCIL FIXED" -Directory $solfacilDir
    
      # Verificar processos
      $running = Check-ProcessRunning -ProcessPattern "tsx"
      if ($running) {
            Write-ColorOutput "`n✅ Scrapers em execução..." "Green"
      }
      else {
            Write-ColorOutput "`n⚠️  Nenhum processo de scraper detectado" "Yellow"
      }
    
      # Verificar se ambos scrapers completaram
      $odexProducts = Get-LatestProducts -Directory $odexDir
      $solfacilProducts = Get-LatestProducts -Directory $solfacilDir
    
      if ($odexProducts -and $solfacilProducts -and 
            $odexProducts.Count -gt 0 -and $solfacilProducts.Count -gt 0) {
        
            Write-ColorOutput "`n`n════════════════════════════════════════════════════════════" "Green"
            Write-ColorOutput " 🎉 EXTRAÇÃO COMPLETA!" "Green"
            Write-ColorOutput "════════════════════════════════════════════════════════════" "Green"
        
            Write-ColorOutput "`n📊 Resumo Final:" "Yellow"
            Write-ColorOutput "   • Odex: $($odexProducts.Count) produtos" "Green"
            Write-ColorOutput "   • Solfácil: $($solfacilProducts.Count) produtos" "Green"
            Write-ColorOutput "   • Total: $($odexProducts.Count + $solfacilProducts.Count) produtos" "Cyan"
            Write-ColorOutput "   • Tempo total: $([math]::Round($elapsed.TotalMinutes, 1)) minutos" "Gray"
        
            break
      }
    
      # Aguardar próxima iteração
      Write-ColorOutput "`n⏳ Próxima verificação em $IntervalSeconds segundos..." "Gray"
      Write-ColorOutput "   (Pressione Ctrl+C para interromper)" "DarkGray"
    
      Start-Sleep -Seconds $IntervalSeconds
}

# Final
if ($iterations -ge $maxIterations) {
      Write-ColorOutput "`n⏰ Tempo limite de monitoramento atingido" "Yellow"
}

Write-ColorOutput "`n✅ Monitoramento encerrado" "Green"
Write-ColorOutput "`nPara ver resultados completos:" "White"
Write-ColorOutput "   Get-ChildItem $odexDir/*.json | Select-Object -Last 1 | Get-Content | ConvertFrom-Json" "Gray"
Write-ColorOutput "   Get-ChildItem $solfacilDir/*.json | Select-Object -Last 1 | Get-Content | ConvertFrom-Json" "Gray"
