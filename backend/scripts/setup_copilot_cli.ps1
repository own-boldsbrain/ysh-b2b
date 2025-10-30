#!/usr/bin/env pwsh
# Setup Script para GitHub Copilot CLI
# Configura o gh copilot extension para automação de desenvolvimento

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Copilot CLI Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if gh CLI is installed
Write-Host "`nChecking for GitHub CLI..." -ForegroundColor Yellow
if (!(Get-Command gh -ErrorAction SilentlyContinue)) {
      Write-Host "GitHub CLI not found. Installing..." -ForegroundColor Red
    
      # Install gh CLI using winget
      if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id GitHub.cli
      }
      else {
            Write-Host "Please install GitHub CLI manually from: https://cli.github.com/" -ForegroundColor Red
            exit 1
      }
}
else {
      Write-Host "✓ GitHub CLI found" -ForegroundColor Green
}

# Check if user is authenticated
Write-Host "`nChecking GitHub authentication..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
      Write-Host "Not authenticated. Starting authentication..." -ForegroundColor Red
      gh auth login
}
else {
      Write-Host "✓ Already authenticated" -ForegroundColor Green
}

# Install GitHub Copilot CLI extension
Write-Host "`nInstalling GitHub Copilot CLI extension..." -ForegroundColor Yellow
gh extension install github/gh-copilot --force

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
$copilotVersion = gh copilot --version 2>&1
if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ GitHub Copilot CLI installed successfully" -ForegroundColor Green
      Write-Host "Version: $copilotVersion" -ForegroundColor Cyan
}
else {
      Write-Host "✗ Installation failed" -ForegroundColor Red
      exit 1
}

# Test Copilot CLI
Write-Host "`nTesting Copilot CLI..." -ForegroundColor Yellow
Write-Host "Running test command: gh copilot suggest 'list files in current directory'" -ForegroundColor Cyan

$testResult = gh copilot suggest "list files in current directory" --target shell 2>&1
if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ Copilot CLI is working" -ForegroundColor Green
}
else {
      Write-Host "✗ Test failed" -ForegroundColor Red
}

# Create alias for easier usage
Write-Host "`nCreating PowerShell aliases..." -ForegroundColor Yellow

$profilePath = $PROFILE.CurrentUserAllHosts
if (!(Test-Path $profilePath)) {
      New-Item -Path $profilePath -ItemType File -Force | Out-Null
}

$aliases = @"

# GitHub Copilot CLI Aliases
function ghcs { gh copilot suggest `$args }
function ghce { gh copilot explain `$args }

"@

Add-Content -Path $profilePath -Value $aliases
Write-Host "✓ Aliases added to PowerShell profile" -ForegroundColor Green
Write-Host "  - ghcs: shortcut for 'gh copilot suggest'" -ForegroundColor Cyan
Write-Host "  - ghce: shortcut for 'gh copilot explain'" -ForegroundColor Cyan

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nQuick Start Examples:" -ForegroundColor Yellow
Write-Host "  gh copilot suggest 'create a docker container'" -ForegroundColor Cyan
Write-Host "  gh copilot explain 'git push origin main'" -ForegroundColor Cyan
Write-Host "`nOr use the shortcuts (restart PowerShell first):" -ForegroundColor Yellow
Write-Host "  ghcs 'your command description'" -ForegroundColor Cyan
Write-Host "  ghce 'command to explain'" -ForegroundColor Cyan
Write-Host "`nFor this project, try:" -ForegroundColor Yellow
Write-Host "  ghcs 'run docker compose for ysh solar project'" -ForegroundColor Cyan
Write-Host "  ghcs 'install python dependencies for web scraping'" -ForegroundColor Cyan
